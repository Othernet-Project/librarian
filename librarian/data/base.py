import functools

from bottle_utils.common import to_bytes

from ..core.contrib.cache.utils import generate_key
from ..core.contrib.databases.utils import row_to_dict
from ..core.exts import ext_container as exts


class CDFObject(object):
    """A generic factory object which gets the data for instantiation by
    attempting to read it from cache first. In case it's not found there, it
    tries to fetch it from database, and if it's not available there either,
    from the filesystem itself.
    """
    DATABASE_NAME = None
    CACHE_KEY_TEMPLATE = None
    ATTEMPT_READ_FROM_FILE = True
    ALLOW_EMPTY_INSTANCES = True

    row_to_dict = staticmethod(row_to_dict)

    def __init__(self, path, data=None, db=None):
        self.path = path
        self._data = row_to_dict(data or dict())
        self._db = db or exts.databases[self.DATABASE_NAME]

    def get_data(self):
        return self._data

    def read_file(self):
        raise NotImplementedError()

    def store(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    @classmethod
    def get_cache_key(cls, path):
        generated = generate_key(path)
        return to_bytes(cls.CACHE_KEY_TEMPLATE.format(generated))

    @classmethod
    def from_file(cls, path, db=None):
        """Read a single entry from file, store it in database and cache the
        data."""
        instance = cls(path, db=db)
        instance.read_file()
        instance.store()
        exts.cache.set(cls.get_cache_key(path), instance.get_data())
        return instance

    @classmethod
    def from_db(cls, paths, immediate=False, db=None):
        """Read multiple entries from database and cache the retrieved raw data.
        If no entries are found in the database, a background task will be
        scheduled to read the data from file."""
        # attempt reading from cache first and collect ids that were not found
        entries = dict()
        remaining = []
        for path in paths:
            key = cls.get_cache_key(path)
            data = exts(onfail=None).cache.get(key)
            entries[path] = data or {}
            if not data:
                remaining.append(path)
        # attempt reading ids that were not found in cache from database in
        # batches, so it won't exceed the parameter limit for very large number
        # of items
        db = db or exts.databases[cls.DATABASE_NAME]
        batches = (remaining[i:i + db.MAX_VARIABLE_NUMBER]
                   for i in range(0, len(remaining), db.MAX_VARIABLE_NUMBER))
        found = set()
        for remaining_batch in batches:
            for (path, data) in cls.fetch(db, remaining_batch):
                entries[path].update(data)
                found.add(path)
        # assemble object instances from gathered data and store them in cache
        instances = dict()
        for (path, data) in entries.items():
            if data or cls.ALLOW_EMPTY_INSTANCES:
                obj = cls(path, data, db=db)
                instances[path] = obj
            # cache only raw data, not object instance
            key = cls.get_cache_key(path)
            exts.cache.set(key, data)
        # ids that were not found neither in cache, nor in the database are
        # scheduled to be read from file
        for path in found.symmetric_difference(remaining):
            if cls.ATTEMPT_READ_FROM_FILE:
                dinfo_gen = functools.partial(cls.from_file, path)
                if immediate:
                    instances[path] = dinfo_gen()
                else:
                    exts.tasks.schedule(dinfo_gen)
            if cls.ALLOW_EMPTY_INSTANCES and path not in instances:
                instances[path] = cls(path, db=db)
        return instances
