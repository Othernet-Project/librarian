"""
Public API for querying and modifying file metadata.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import functools
import logging
import os

from ...core.exts import ext_container as exts
from ...core.utils import batched, as_iterable
from .contenttypes import ContentTypes
from .processors import Processor, DIRECTORY_TYPE, FILE_TYPE
from .utils import ancestors_of
from .wrapper import MetaWrapper


class FSWriter(object):
    """
    Create or update a file system object while guaranteeing that all
    non-existent ancestors of it will be created as well. These operation are
    performed on the database level only, no actual file system objects would
    be created.
    """
    #: Database table name
    FS_TABLE = 'fs'
    #: Columns belonging to ``FS_TABLE``
    FS_COLUMNS = ('parent_id', 'path', 'type', 'mime_type', 'content_types')
    #: Default content type (applies for all fs entries)
    DEFAULT_CONTENT_TYPE = ContentTypes.to_bitmask(ContentTypes.GENERIC)
    #: Prefix to be used when the whole range needs to be invalidated
    CACHE_PREFIX = 'fs_'
    #: Sensible timeout since fs entries are not needed to be cached forever
    CACHE_TIMEOUT = 60 * 60
    #: Default root entry in case not even the root ancestor is found
    DEFAULT_ROOT = dict(id=0)

    def __init__(self, data, db, cache):
        self._db = db
        self._cache = cache
        # unpack data
        self._path = data['path']
        if self._path:
            self._path = os.path.normpath(self._path)
        self._parent_path = os.path.dirname(self._path)
        self._type = data['type']
        self._mime_type = data['mime_type']
        self._content_types = data['content_types']

    @classmethod
    def key(cls, path):
        """
        Return the unique key under which the file system object can be cached.
        """
        return cls.CACHE_PREFIX + path

    def _get_chain(self):
        """
        Get all ancestor file system objects of the object being created or
        updated by first searching for them in cache, and falling back to
        database lookup.
        """
        ancestors = []
        missing = []
        path_chain = list(ancestors_of(self._path))
        for (i, path) in enumerate(path_chain):
            entry = self._cache.get(self.key(path))
            # in the event of the first missing entry from cache, abort
            # further lookup in it, since it's not possible to have a child
            # whithout it's parent stored, so none of the children would
            # exist either
            if not entry:
                missing = path_chain[i:]
                break
            # append to list of found ancestors
            ancestors.append(entry)
        # in case all entries were found in cache, no db lookup is needed
        if not missing:
            return (ancestors, missing)
        # fetch entries not found in cache from database
        query = self._db.Select(sets=self.FS_TABLE,
                                where=self._db.sqlin('path', missing),
                                order='length(path)')
        for entry in self._db.fetchiter(query, missing):
            path = entry['path']
            self._cache.set(self.key(path),
                            dict(entry),
                            timeout=self.CACHE_TIMEOUT)
            ancestors.append(entry)
            missing.remove(path)
        # if missing is still not empty, those entries need to be created
        return (ancestors, missing)

    def _fetch(self, path):
        """
        Return file system object matching ``path`` from the database.
        """
        query = self._db.Select(sets=self.FS_TABLE, where='path=%s')
        return dict(self._db.fetchone(query, (path,)))

    def _create(self, path, parent_id, fs_type, mime_type, content_types):
        """
        Create a new file system object based on the passed in parameters,
        cache it and return the freshly created object.
        """
        query = self._db.Replace(self.FS_TABLE,
                                 constraints=['path'],
                                 cols=self.FS_COLUMNS)
        self._db.execute(query, dict(path=path,
                                     parent_id=parent_id,
                                     type=fs_type,
                                     mime_type=mime_type,
                                     content_types=content_types))
        # fetch newly created entry, store it in cache and return it
        entry = self._fetch(path)
        self._cache.set(self.key(path), entry, timeout=self.CACHE_TIMEOUT)
        return entry

    def _update(self, path, content_types, overwrite=False):
        """
        Update the ``content_types`` column of the file system object matching
        the passed in ``path``.
        """
        cache_key = self.key(path)
        entry = self._cache.get(cache_key)
        if (entry and not overwrite and
                entry['content_types'] & content_types == content_types):
            # the cached version of entry already contained the specified
            # content type, so another update is not necessary
            return entry
        # entry was either not yet in cache, or the cached version did not have
        # the specified ``content_type`` yet
        if overwrite:
            what = dict(content_types='%(content_types)s')
        else:
            what = dict(content_types='content_types | %(content_types)s')
        query = self._db.Update(self.FS_TABLE, where='path = %(path)s', **what)
        self._db.execute(query, dict(path=path, content_types=content_types))
        if not entry or overwrite:
            # entry was not in cache previously, or it's content type was
            # rewritten from scratch, so fetch it now
            entry = self._fetch(path)
        else:
            # entry was in cache and it's content type can be reliably
            # predicted, so just update it's content_types to match the
            # above performed update
            entry['content_types'] |= content_types
        # store updated entry in cache and return it
        self._cache.set(cache_key, entry, timeout=self.CACHE_TIMEOUT)
        return entry

    def write(self):
        """
        Create or update a file system object based on data that was passed to
        the constructor and return it's current representation after the
        operations are performed.
        """
        (found, missing_paths) = self._get_chain()
        last = found[-1] if found else self.DEFAULT_ROOT
        for missing in missing_paths:
            content_types = self.DEFAULT_CONTENT_TYPE
            # set needed content type only for target ``path`` itself
            # and it's direct parent (if ``path`` is a file), not for any
            # other ancestor
            if (missing == self._path or (missing == self._parent_path and
                                          self._type == FILE_TYPE)):
                content_types |= self._content_types
            # type of object is a directory for all ancestors except the path
            # being created which was specified already explicitly
            if missing == self._path:
                fs_type = self._type
                mime_type = self._mime_type
            else:
                fs_type = DIRECTORY_TYPE
                mime_type = None
            # in each next iteration the now created fs object will be
            # referenced as the parent object
            last = self._create(missing,
                                last['id'],
                                fs_type,
                                mime_type,
                                content_types)
        # update content types on parent if it was not created now and only if
        # the fs entry being created is a file, since ``content_types`` on a
        # directory entry should reflect only the content types of the files
        # that it contains
        if self._parent_path not in missing_paths and self._type == FILE_TYPE:
            self._update(self._parent_path, self._content_types)
        # update only the content types on fs entry if it already existed
        if self._path not in missing_paths:
            last = self._update(self._path,
                                self._content_types,
                                overwrite=self._type == DIRECTORY_TYPE)
        # returning the either now created or updated fs entry for ``path``
        return last

    def update(self):
        """
        Attempt to perform just an update of ``content_types`` on the file
        system object desribed by data that was passed to the constructor.
        This is an unsafe method, and should be used only when it's guaranteed
        that the file system object already exists.
        """
        return self._update(self._path, self._content_types)



class Archive(object):
    """
    Provides API for querying and writing file metadata.

    Queries can occur either for a set of paths or for paths under a specific
    directory. For paths which metadata is not found, the processing will be
    scheduled to run asynchronously, while quickly attainable, placeholder
    data is returned instead.
    """

    #: Aliases for imported classes
    ContentTypes = ContentTypes
    Processor = Processor
    MetaWrapper = MetaWrapper
    FSWriter = FSWriter
    #: Database name
    DATABASE_NAME = 'librarian'
    #: Database tables
    FS_TABLE = 'fs'
    META_TABLE = 'meta'
    #: Database colums
    META_COLUMNS = ('fs_id', 'language', 'key', 'value')
    #: Default root path, relative to FSAL's base directory
    ROOT_PATH = ''
    #: Events
    ENTRY_POINT_FOUND = 'entry_point_found'
    #: Special metadata type that originates from automatic analysis
    AUTO_DEDUCED = '__auto__'

    def __init__(self, **kwargs):
        self._db = kwargs.get('db', exts.databases[self.DATABASE_NAME])
        self._config = kwargs.get('config', exts.config)
        self._fsal = kwargs.get('fsal', exts.fsal)
        self._cache = kwargs.get('cache', exts.cache)
        self._tasks = kwargs.get('tasks', exts.tasks)
        self._events = kwargs.get('events', exts.events)
        self._events.subscribe(self.ENTRY_POINT_FOUND, self._entry_point_found)
        # Select what from meta table
        self._meta_what = ','.join('{}.{}'.format(self.META_TABLE, c)
                                   for c in self.META_COLUMNS)

    def _analyze(self, path, partial):
        """
        Return found metadata for ``path``.

        Called by the public py:meth:`~Archive.analyze` method and performs
        the heavy lifting to obtain and return metadata.
        """
        logging.debug(u"Analyze[%s] %s", ('FULL', 'PARTIAL')[partial], path)
        data = dict()
        for proc_cls in self.Processor.for_path(path):
            proc = proc_cls(path, data=data, partial=partial, fsal=self._fsal)
            # store entry point on parent folder if available
            if proc_cls.is_entry_point(path):
                content_type = self.ContentTypes.to_bitmask(proc_cls.name)
                self._events.publish(self.ENTRY_POINT_FOUND,
                                     path=path,
                                     content_type=content_type,
                                     processor=proc_cls)
            # gather metadata from current processor into ``data``
            proc.process()
        # return gathered metadata wrapped in py:class:`MetaWrapper`
        return dict((k, self.MetaWrapper(v)) for (k, v) in data.items())

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=100, aggregator=batched.updater)
    def analyze(self, paths, partial=False, callback=None):
        """
        Analyze ``paths`` to determine their content type and metadata.

        A comprehensive analysis will be performed only if ``partial`` is not
        set, which also write the found metadata into the database. Otherwise,
        if partial is set, it will perform a quick analysis and return only
        basic information about the paths. The optional ``callback`` argument
        determines if the analysis will run asynchronously, invoking the
        ``callback`` function with the obtained data, or in blocking mode,
        returning the data.
        """
        if not callback:
            ret_val = dict()
            for path in paths:
                ret_val.update(self._analyze(path, partial))
            return ret_val
        # schedule background task to perform analysis of ``paths``
        self._tasks.schedule(lambda: callback(self.analyze(paths, partial)))
        return {}

    def _scan(self, path, partial, callback, maxdepth, depth, delay):
        """
        Recursively scan ``path`` and analyze all found entries.

        Called by the public py:meth:`~Archive.scan` method and performs
        the heavy lifting to traverse the directory tree and callback or
        yield the results of py:meth:`~Archive.analyze`.
        """
        path = path or self.ROOT_PATH
        (success, dirs, files) = self._fsal.list_dir(path or '.')
        if not success:
            logging.warning(u"Scan stopped. Invalid path: '%s'", path)
            raise StopIteration()
        # schedule paths to be analyzed, in the same blocking manner
        file_paths = (fso.rel_path for fso in files)
        metadata = self.analyze(file_paths, partial=partial)
        if callback:
            callback(metadata)
        else:
            yield metadata
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
                for metadata in self._scan(**kwargs):
                    yield metadata

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

    def _keep_supported(self, paths, content_type):
        """
        Return a list of only those ``paths`` that belong to ``content_type``.
        """
        processor_cls = self.Processor.for_type(content_type)
        return [path for path in paths if processor_cls.can_process(path)]

    def _strip(self, metadata, content_type=None):
        """
        Return a copy of the passed in ``metadata`` with those keys stripped
        out that do not belong to the specified ``content_type``.
        """
        keys = self.ContentTypes.keys(content_type)
        return dict((k, v) for (k, v) in metadata.items() if k in keys)

    def _reconstruct_meta(self, rows):
        """
        Return py:attr:`~Archive.MetaWrapper` instances created from ``rows``.

        ``rows`` is expected to be ordered by the ``path`` column.
        """
        path = data = None
        for row in rows:
            # path changed, so row belongs to a different fs entry
            if row['path'] != path:
                # yield previous data element before creating the new one
                if data:
                    yield self.MetaWrapper(data)
                # create next fs object
                path = row['path']
                data = dict(path=path,
                            id=row['id'],
                            parent_id=row['parent_id'],
                            type=row['type'],
                            mime_type=row['mime_type'],
                            content_types=row['content_types'],
                            metadata={})
            # put meta key/value pairs into fs data element
            key = row['key']
            if key:
                language = row['language']
                data['metadata'].setdefault(language, {})
                data['metadata'][language][key] = row['value']
        # yield last item
        if data:
            yield self.MetaWrapper(data)

    def for_parent(self, path, content_type=None):
        """
        Return a dict of {path: metadata} mapping for all direct children of
        ``path``, optionally filtered for a specific ``content_type``.
        """
        query = self._db.Select('fsr.*, {}'.format(self._meta_what),
                                sets=self.FS_TABLE,
                                where='fs.path = %(path)s',
                                order='fsr.path')
        query.sets.join('fs fsr', on='fsr.parent_id = fs.id')
        query.sets.join(self.META_TABLE,
                        kind='LEFT OUTER',
                        on='meta.fs_id = fsr.id')
        params = dict(path=path)
        if content_type:
            # bitwise filter metadata for specific content type
            query.where += ('(fsr.content_types & %(content_type)s)'
                            ' = %(content_type)s')
            bitmask = self.ContentTypes.to_bitmask(content_type)
            params.update(content_type=bitmask)
        row_iter = self._db.fetchiter(query, params)
        return dict((meta.path, meta)
                    for meta in self._reconstruct_meta(row_iter))

    def _attach_missing(self, paths, data, partial):
        """
        Find the difference between the passed in ``paths`` and the found
        entries ``data``. Paths that are not present in ``data`` should be
        analyzed in-place in either blocking or partial mode, depending on
        the state of the ``partial`` flag.
        """
        # get set of paths not found in query results
        missing = set(paths).difference(data.keys())
        # return early because there are no missing entries
        if not missing:
            return data
        # there are missing entries, find them before returning
        if not partial:
            # perform deep scan in blocking mode and wait while the results
            # are obtained and stored
            metas = self.analyze(missing)
            self.save_many(metas)
            data.update(metas)
            return data
        # schedule missing entries to be analyzed asynchronously and their
        # meta information stored in database, but while that information
        # becomes available, return quickly attainable basic information for
        # them as placeholders
        self.analyze(missing, callback=self.save_many)
        # fetch partials quickly
        partials = self.analyze(missing, partial=True)
        data.update(partials)
        return data

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=999, aggregator=batched.updater)
    def get(self, paths, content_type=None, partial=True, ignore_missing=False):
        """
        Return a dict of {path: metadata} mapping for the passed in ``paths``.

        The result may be optionally filtered for a specific ``content_type``.
        """
        if content_type:
            # of the paths passed in, some might be unusable by the chosen
            # ``content_type``, filter those out
            paths = self._keep_supported(paths, content_type)
            # return early in case all ``paths`` dropped out in filtering
            if not paths:
                return {}
        # prepare query
        query = self._db.Select('fs.*, {}'.format(self._meta_what),
                                sets=self.META_TABLE,
                                where=self._db.sqlin('fs.path', paths),
                                order='fs.path')
        query.sets.join(self.FS_TABLE,
                        kind='RIGHT OUTER',
                        on='fs.id = meta.fs_id')
        # if no ``content_type`` was given, no copy will be made
        params = paths
        if content_type:
            # bitwise filter metadata for specific content type
            query.where += '(fs.content_types & %s) = %s'
            bitmask = self.ContentTypes.to_bitmask(content_type)
            params = list(paths) + [bitmask, bitmask]
        row_iter = self._db.fetchiter(query, params)
        data = dict((meta.path, meta)
                    for meta in self._reconstruct_meta(row_iter))
        # return early in case only the really existing entries are needed
        if ignore_missing:
            return data
        # add missing entries to ``data`` and return with complete information
        return self._attach_missing(paths, data, partial)

    def parent(self, path, refresh=False):
        """
        For a given ``path`` to a directory, return the stored folder entry.
        The folder entry can be used to obtain all the detected content types
        among it's file entries, and to optionally get a ``main``(filename)
        that represents the entry point for more complex content. ``refresh``
        can either be a flag, indicating a need for a fresh scan, or a dict
        of earlier scan results, which will be used instead of performing the
        scan in-place.
        """
        if refresh:
            return self._refresh_parent(path, refresh)
        # attempt getting existing data
        metadata = self.get(path, ignore_missing=True)
        if metadata:
            # no need for the path:metadata dict, return only meta wrapper
            return metadata[path]
        # no existing data found, perform blocking scan now
        return self._refresh_parent(path)

    def _refresh_parent(self, path, source=None):
        """
        Perform a blocking partial scan of only the folder being queried
        without going any deeper. If ``source`` is a dict, it will be assumed
        that it has the same format as regular scan results, and will be used
        to update the directory entry.
        """
        if isinstance(source, dict):
            metas = source
        else:
            (metas,) = self.scan(path, partial=True, maxdepth=0)
        # prepare iterator over content_type values only
        itypes = (m.content_types for m in metas.values())
        default = self.ContentTypes.to_bitmask(self.ContentTypes.GENERIC)
        # calculate bitmask for the whole folder
        bitmask = functools.reduce(lambda acc, x: acc | x, itypes, default)
        raw_data = dict(path=path,
                        type=DIRECTORY_TYPE,
                        mime_type=None,
                        content_types=bitmask)
        self.save(raw_data)
        return self.get(path)[path]

    def search(self, terms, content_type=None, language=None):
        """
        Perform a text based search over metadata and return found entries.

        Result may be optionally filtered for a specific ``content_type``
        (which also limits the scope of search to fields only relevant to the
        chosen ``content_type`` and / or for a specific ``language``.
        Due to the nature of the search query, not all metadata belonging to
        the found fs entries will be present on the combined meta object, only
        those that were search actually searched for (``search_keys``).
        """
        query = self._db.Select('fs.*, {}'.format(self._meta_what),
                                sets=self.META_TABLE,
                                order='fs.path')
        keys = self.ContentTypes.search_keys(content_type)
        if keys:
            # safe string interpolation, as only column names are being added
            # from a local source, not user provided data
            filters = ' OR '.join("key = '{}' AND value ILIKE %(terms)s".format(k)
                                  for k in keys)
            query.where += '({})'.format(filters)
        # join condition may be extended below
        join_on = "meta.fs_id = fs.id"
        params = dict(terms='%' + terms.lower() + '%')
        # add language filter if specified (must be checked against ``None``
        # because ``NO_LANGUAGE`` value is an empty string
        if language is not None:
            query.where += 'meta.language = %(language)s'
            params.update(language=language)
        # add content type filter if specified
        if content_type:
            # bitwise filter metadata for specific content type
            join_on += ' AND (fs.content_types & %(bitmask)s) = %(bitmask)s'
            params.update(bitmask=self.ContentTypes.to_bitmask(content_type))
        query.sets.join(self.FS_TABLE, on=join_on)
        row_iter = self._db.fetchiter(query, params)
        return dict((meta.path, meta)
                    for meta in self._reconstruct_meta(row_iter))

    def _entry_point_found(self, path, content_type, processor):
        """
        Store on the parent directory of ``path`` the filename of the found
        entry point.
        """
        parent_path = os.path.dirname(path)
        new = os.path.basename(path)
        results = self.get(parent_path, ignore_missing=True)
        data = results[parent_path].unwrap() if results else {}
        metadata = data.get('metadata', {})
        metadata.setdefault(self.AUTO_DEDUCED, {})
        old = metadata[self.AUTO_DEDUCED].get('main')
        # check if newly found path is a better candidate than the existing
        if not processor.is_entry_point(old=old, new=path):
            return
        # new candidate is indeed better, store it
        metadata[self.AUTO_DEDUCED].update(main=new)
        self.save(dict(path=parent_path,
                       metadata=metadata,
                       type=DIRECTORY_TYPE,
                       mime_type=None,
                       content_types=content_type))

    def _save_metadata(self, fs_id, metadata):
        """
        Store the passed in ``metadata`` associated with the fs object under
        ``fs_id``.
        """
        query = self._db.Replace(self.META_TABLE,
                                 constraints=['fs_id', 'language', 'key'],
                                 cols=self.META_COLUMNS)
        cleaned = dict()
        for (language, section) in metadata.items():
            cleaned[language] = self._strip(section)
            # transform dict of metadata section into a sequence of dicts with
            # key-value pairs representing each pair from ``cleaned_section``
            seq = (dict(key=key, value=value, language=language, fs_id=fs_id)
                   for (key, value) in cleaned[language].items())
            self._db.executemany(query, seq)
        # stripped / cleaned version of passed in ``metadata`` will be returned
        return cleaned

    def save(self, data):
        """
        Store the passed in ``data``, dropping any keys that are not in the
        specification.
        """
        # unwrap ``data`` if needed
        if isinstance(data, self.MetaWrapper):
            data = data.unwrap()
        # save file system data
        fs_writer = self.FSWriter(data, db=self._db, cache=self._cache)
        saved = fs_writer.write()
        # replace metadata associated with fs object with cleaned version
        saved['metadata'] = self._save_metadata(saved['id'],
                                                data.get('metadata', {}))
        logging.debug(u"Metadata stored for %s", saved['path'])
        return self.MetaWrapper(saved)

    def save_many(self, metas):
        """
        Helper method that can accept the structure produced by most of the
        query methods, e.g. py:meth:`~Archive.analyze`, and invoke for each
        path:data pair from ``metas`` the py:meth:`~Archive.save` method.
        """
        # ``executemany`` would be a better fit instead of individual saves,
        # but since we rely on the folder id as well, it's not doable just now
        for data in metas.values():
            self.save(data)

    @as_iterable(params=[1])
    @batched(arg=1, batch_size=999, lazy=False)
    def remove(self, paths):
        """
        Delete the passed in `paths` from the metadata database and run cleanup
        routines if needed.
        """
        # perform optional cleanup by processor(s)
        for path in paths:
            for proc_cls in self.Processor.for_path(path):
                proc_cls(path, fsal=self._fsal).deprocess()
            # invalidate cached entries
            self._cache.delete(self.FSWriter.key(path))
        # first delete metadata by joining on fs table
        query = self._db.Delete('{} USING {}'.format(self.META_TABLE,
                                                     self.FS_TABLE),
                                where='meta.fs_id = fs.id')
        query.where += self._db.sqlin('fs.path', paths)
        self._db.execute(query, paths)
        # after metadata is deleted, fs entries can be deleted safely
        query = self._db.Delete(self.FS_TABLE,
                                where=self._db.sqlin('path', paths))
        self._db.execute(query, paths)
        # after deleting meta entries, the contenttypes column of the parent
        # folder needs to be recalculated
        for parent_path in set(os.path.dirname(path) for path in paths):
            # do not refresh parent if it was deleted
            if parent_path not in paths:
                self._refresh_parent(parent_path)

    def clear_and_reload(self):
        """
        Empty metadata database and start reindexing the whole content
        directory from scratch.
        """
        with self._db.transaction():
            self.clear()
            # as this method is most likely going to be invoked only by the
            # command handler, it must be a blocking scan
            for metas in self.scan():
                self.save_many(metas)

    def clear(self):
        """
        Empty meta database. It deletes all data. Really everything.
        """
        query = self._db.Delete(self.META_TABLE)
        self._db.execute(query)
        query = self._db.Delete(self.FS_TABLE)
        self._db.execute(query)
