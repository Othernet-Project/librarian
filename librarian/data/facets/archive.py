import functools
import logging
import os

from ...core.exts import ext_container as exts
from ...core.utils import batched, as_iterable
from .facettypes import FacetTypes
from .processors import Processor


class Archive(object):
    """
    Facet data manager, trying to perform the following tasks:

    - get applicable facet types for a given set of paths
    - get facet data for a specific facet type over a given set of paths
    - when requesting specific facet data for a set of paths, compare the
      returned entries, and for each missing one return a brief - quickly
      constructible version of data, and schedule a background task to
      parse the more expensive parts of it to be written into the database
    """
    DATABASE_NAME = 'facets'
    #: Database tables
    FACETS_TABLE = 'facets'
    FOLDERS_TABLE = 'folders'
    #: Database columns for folders
    FOLDERS_KEYS = ('path', 'facet_types', 'main')
    #: Default root path, relative to FSAL's base directory
    ROOT_PATH = '.'
    #: Aliases for imported classes
    FacetTypes = FacetTypes
    Processor = Processor

    def __init__(self, **kwargs):
        self._db = kwargs.get('db', exts.databases.facets)
        self._config = kwargs.get('config', exts.config)
        self._fsal = kwargs.get('fsal', exts.fsal)
        self._tasks = kwargs.get('tasks', exts.tasks)

    def _analyze(self, path, partial, callback):
        """
        Called by the public py:meth:`~Archive.analyze` method and performs
        the heavy lifting to obtain and return facet data, with optionally
        invoking a ``callback`` function with obtained facet data, if it was
        specified.
        """
        logging.debug(u"Analyze[%s] %s", ('FULL', 'PARTIAL')[partial], path)
        data = dict()
        for proc_cls in self.Processor.for_path(path):
            # store entry point on parent folder if available
            if proc_cls.is_entry_point(path):
                main = os.path.basename(path)
                parent = os.path.dirname(path)
                bitmask = self.FacetTypes.to_bitmask(proc_cls.name)
                self._save_parent(parent, main=main, facet_types=bitmask)
            # gather metadata from current processor into ``data``
            proc_cls(self._fsal).process_file(path, data=data, partial=partial)
        # invoke specified ``callback`` if available with gathered metadata
        # and then return the same
        if callback:
            callback(data)
        return data

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=10, aggregator=batched.updater)
    def analyze(self, paths, partial=False, callback=None):
        """
        Analyze the given ``paths`` to determine which facet types can handle
        them, write the found information into the database and if the flag
        ``partial`` is set, return efficiently attainable basic information
        about the paths. The optional ``callback`` argument determines if the
        analysis will run asynchronously, invoking the ``callback`` function
        with the obtained data, or in blocking mode, returning the data.
        """
        if not callback:
            return dict((path, self._analyze(path, partial, callback))
                        for path in paths)
        # schedule background task to perform analysis of ``paths``
        fn = functools.partial(self._analyze,
                               partial=partial,
                               callback=callback)
        self._tasks.schedule(lambda paths: map(fn, paths), args=(paths,))
        return {}

    def _scan(self, path, partial, callback, maxdepth, depth, delay):
        """
        Called by the public py:meth:`~Archive.scan` method and performs
        the heavy lifting to traverse the directory tree and callback or
        yield the results of py:meth:`~Archive.analyze`.
        """
        path = path or self.ROOT_PATH
        (success, dirs, files) = self._fsal.list_dir(path)
        if not success:
            logging.warn(u"Scan stopped. Invalid path: '{}'".format(path))
            raise StopIteration()
        # schedule paths to be analyzed, in the same blocking manner
        file_paths = (fso.rel_path for fso in files)
        facets = self.analyze(file_paths, partial=partial)
        if callback:
            callback(facets)
        else:
            yield facets
        # if we reached specified ``maxdepth``, do not go any deeper
        if maxdepth is not None and depth == maxdepth:
            raise StopIteration()
        # scan subfolders
        for fso in dirs:
            kwargs = dict(path=fso.rel_path,
                          partial=partial,
                          callback=callback,
                          maxdepth=maxdepth,
                          depth=depth + 1,
                          delay=delay)
            if callback:
                self._tasks.schedule(self.scan, kwargs=kwargs, delay=delay)
            else:
                for facets in self._scan(**kwargs):
                    yield facets

    def scan(self, path=None, partial=False, callback=None, maxdepth=None,
             depth=0, delay=0):
        """
        Traverse ``path`` and py:meth:`~Archive.analyze` all encountered files.
        In case ``callback`` is specified, the traversing will be performed
        asynchronously, with each next level scheduled as a separate background
        task, and invoking ``callback`` with each result set separately. If
        ``callback`` was not specified, it will behave as an iterator, yielding
        the results of scan on each level. ``delay`` is used only in async mode
        and it represents the amount of seconds before the next directory is to
        be scanned. ``maxdepth`` can limit how deep the scan is allowed to
        traverse directory tree.
        """
        generator = self._scan(path, partial, callback, maxdepth, depth, delay)
        if callback:
            # evaluate generator(because no-one else will) so that ``callback``
            # actually gets executed
            return list(generator)
        # return unevaluated generator
        return generator

    def _keep_supported(self, paths, facet_type):
        """
        Return a list of only those ``paths`` that belong to ``facet_type``.
        """
        processor_cls = self.Processor.for_type(facet_type)
        return [path for path in paths if processor_cls.can_process(path)]

    @classmethod
    def strip(cls, facet_data, facet_type):
        """
        Return a copy of the passed in ``facet_data`` with those keys stripped
        out that do not belong to the specified ``facet_type``.
        """
        keys = cls.FacetTypes.keys(facet_type)
        return dict((k, v) for (k, v) in facet_data.items() if k in keys)

    def parent(self, path):
        """
        For a given ``path`` to a directory, return the stored folder entry.
        The folder entry can be used to obtain all the detected facet types
        among it's file entries, and to optionally get a ``main``(filename)
        that represents the entry point for more complex content.
        """
        q = self._db.Select(sets=self.FOLDERS_TABLE, where='path = %(path)s')
        folder = self._db.fetchone(q, dict(path=path))
        if not folder:
            # perform a blocking partial scan of only the folder being queried
            # without going any deeper
            (facets,) = self.scan(path, partial=True, maxdepth=0)
            # prepare iterator over facet_type values only
            itypes = (f['facet_types'] for f in facets.values())
            default = self.FacetTypes.to_bitmask(self.FacetTypes.GENERIC)
            # calculate bitmask for the whole folder
            bitmask = functools.reduce(lambda acc, x: acc | x, itypes, default)
            folder = self._save_parent(path, facet_types=bitmask)
        # found folder entry, return relevant information only
        names = self.FacetTypes.from_bitmask(folder['facet_types'])
        return dict(facet_types=names, path=path, main=folder['main'])

    def for_parent(self, path, facet_type=None):
        """
        Return a dict of {path: facet data} mapping for all direct children of
        ``path``, optionally filtered for a specific ``facet_type``.
        """
        q = self._db.Select('facets.*',
                            sets=self.FACETS_TABLE,
                            where='folders.path = %s')
        q.sets.join(self.FOLDERS_TABLE, on='facets.folder = folders.id')
        params = [path]
        if facet_type:
            # bitwise filter facet data for specific facet type
            q.where += '(facets.facet_types & %s) = %s'
            bitmask = self.FacetTypes.to_bitmask(facet_type)
            params += [bitmask, bitmask]
        return dict((row['path'], row)
                    for row in self._db.fetchiter(q, params))

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=999, aggregator=batched.updater)
    def get(self, paths, facet_type=None):
        """
        Return a dict of {path: facet data} mapping for the passed in ``paths``
        and optionally filtered for a specific ``facet_type``.
        """
        if facet_type:
            # of the paths passed in, some might be unusable by the chosen
            # ``facet_type``, filter those out
            paths = self._keep_supported(paths, facet_type)
        # prepare query
        q = self._db.Select(sets=self.FACETS_TABLE,
                            where=self._db.sqlin('path', paths))
        params = paths  # if no ``facet_type`` was given, no copy will be made
        if facet_type:
            # bitwise filter facet data for specific facet type
            q.where += '(facet_types & %s) = %s'
            bitmask = self.FacetTypes.to_bitmask(facet_type)
            params = list(paths) + [bitmask, bitmask]
        data = dict((row['path'], row)
                    for row in self._db.fetchiter(q, params))
        # get set of paths not found in query results
        missing = set(paths).difference(data.keys())
        # schedule missing entries to be analyzed and their meta information
        # stored in database, but while that information becomes available,
        # return quickly attainable basic information for them as placeholders
        if missing:
            # schedule background deep scan of missing paths
            self.analyze(missing, callback=self.save)
            # fetch partials quickly
            partials = self.analyze(missing, partial=True)
            data.update(partials)
        return data

    def search(self, terms, facet_type=None):
        """
        Perform a text based search for facet data, with optionally filtering
        for a specific ``facet_type`` (which also limits the scope of search
        to fields relevant to the chosen ``facet_type``.
        """
        q = self._db.Select(sets=self.FACETS_TABLE)
        cols = self.FacetTypes.search_keys(facet_type)
        # safe string interpolation, as only column names are being added from
        # a local source, not user provided data
        filters = ' OR '.join('{} ILIKE %(terms)s'.format(c) for c in cols)
        q.where += '({})'.format(filters)
        params = dict(terms='%' + terms.lower() + '%')
        if facet_type:
            # bitwise filter facet data for specific facet type
            q.where += '(facet_types & %(bitmask)s) = %(bitmask)s'
            bitmask = self.FacetTypes.to_bitmask(facet_type)
            params.update(bitmask=bitmask)
        return dict((row['path'], row)
                    for row in self._db.fetchiter(q, params))

    def _save_parent(self, path, **kwargs):
        """
        Find the folder entry by the given ``path`` and update it's values
        with given data in ``kwargs``. If the folder entry does not exist
        yet, create it. In both cases, return the folder object.
        """
        clean = dict((k, v) for (k, v) in kwargs.items()
                     if k in self.FOLDERS_KEYS)
        q = self._db.Select(sets=self.FOLDERS_TABLE, where='path = %s')
        folder = self._db.fetchone(q, (path,))
        if not folder:
            # no folder entry, create it now
            clean.update(path=path)
            q = self._db.Insert(self.FOLDERS_TABLE, cols=clean.keys())
            self._db.execute(q, clean)
            # fetch newly created folder
            q = self._db.Select(sets=self.FOLDERS_TABLE, where='path = %s')
            return self._db.fetchone(q, (path,))
        # folder entry found, just update existing data
        cols = dict((k, '%({})s'.format(k)) for k in clean.keys())
        q = self._db.Update(self.FOLDERS_TABLE,
                            where='path = %(path)s',
                            **cols)
        # copy original folder data
        to_update = dict(folder)
        facet_types = clean.pop('facet_types', 0)
        main = clean.pop('main', None)
        # if main is specified, check if existing one scores higher maybe
        if main and facet_types:
            # when main is being changed, ``facet_types`` always represents
            # a single type
            (facet_type,) = self.FacetTypes.from_bitmask(facet_types)
            # write new main only if it has higher score than existing
            proc_cls = self.Processor.for_type(facet_type)
            if proc_cls.is_entry_point(main, to_update.get('main')):
                # new main scored higher than existing, use it
                clean.update(main=main)
        # add new bitmask value to existing (if specified)
        facet_types |= to_update['facet_types']
        # update folder data with new values
        to_update.update(facet_types=facet_types, path=path, **clean)
        self._db.execute(q, to_update)
        return to_update

    def save(self, data):
        """
        Store the passed in facet data, dropping any keys that are not in
        the specification.
        """
        cleaned_data = dict((k, v) for (k, v) in data.items()
                            if k in self.FacetTypes.keys())
        # update parent folder's bitmask and fetch it's id
        parent = os.path.dirname(cleaned_data['path'])
        folder = self._save_parent(parent,
                                   facet_types=cleaned_data['facet_types'])
        # now that folder id is available, save the facet entry
        cleaned_data['folder'] = folder['id']
        q = self._db.Replace(self.FACETS_TABLE,
                             constraints=['path'],
                             cols=cleaned_data.keys())
        self._db.execute(q, cleaned_data)
        logging.debug(u"Facet data stored for %s", cleaned_data['path'])
        return cleaned_data

    def save_many(self, facets):
        """
        Helper method that can accept the structure produced by most of the
        query methods, e.g. py:meth:`~Archive.analyze`, and invoke for each
        path:data pair from ``facets`` the py:meth:`~Archive.save` method.
        """
        # ``executemany`` would be a better fit instead of individual saves,
        # but since we rely on the folder id as well, it's not doable just now
        for data in facets.values():
            self.save(data)

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=999, lazy=False)
    def remove(self, paths):
        """
        Delete the passed in `paths` from the facets database and run cleanup
        routines if needed.
        """
        # perform optional cleanup by processor(s)
        for path in paths:
            for proc_cls in self.Processor.for_path(path):
                proc_cls().deprocess_file(path)
        # remove entries from database
        q = self._db.Delete(self.FACETS_TABLE,
                            where=self._db.sqlin('path', paths))
        self._db.execute(q, paths)

    def clear_and_reload(self):
        """
        Empty facets database and start reindexing the whole content directory
        from scratch.
        """
        with self._db.transaction():
            self.clear()
            # as this method is most likely going to be invoked only by the
            # command handler, it must be a blocking scan
            for facets in self.scan():
                self.save_many(facets)

    def clear(self):
        """
        Empty facets database. It deletes all data. Really everything.
        """
        q = self._db.Delete(self.FACETS_TABLE)
        self._db.execute(q)
