import itertools
import os
import re

from ..core.exts import ext_container as exts
from .meta.archive import Archive


class Error(Exception):
    """
    Base class for all :py:class:`Manager` related exceptions.
    """
    pass


class InvalidQuery(Error):
    """
    Raised when an invalid path or search query is passed to one of the query
    methods on :py:class:`Manager`.
    """
    pass


class Manager(object):
    """
    Provides a facade over various lower level APIs, such as the file system
    abstraction layer and the Meta py:class:`Archive` facilities. The
    objects returned through it's API provide convenient access to all the
    queried data appropriately connected together.
    """
    #: Exception classes
    Error = Error
    InvalidQuery = InvalidQuery
    #: Alias for py:attr:`Archive.ROOT_PATH`
    ROOT_PATH = Archive.ROOT_PATH
    #: Match any string that starts with a period, or has at least one path
    #: separator followed by a period
    RE_PATH_WITH_HIDDEN = re.compile(r'^(\.|.*{}\.)'.format(os.sep))

    def __init__(self, **kwargs):
        self._fsal = kwargs.get('fsal', exts.fsal)
        self._config = kwargs.get('config', exts.config)
        self._databases = kwargs.get('databases', exts.databases)
        self._archive = Archive(db=self._databases.meta,
                                config=self._config,
                                fsal=self._fsal,
                                cache=kwargs.get('cache', exts.cache),
                                tasks=kwargs.get('tasks', exts.tasks),
                                events=kwargs.get('events', exts.events))

    def get_root(self):
        """
        Return the root path as specified in py:class:`Archive`.
        """
        return self.ROOT_PATH

    def _is_hidden(self, fso):
        """
        Return whether the given ``fso`` is hidden or not.
        """
        return self.RE_PATH_WITH_HIDDEN.match(fso.rel_path)

    def _filter_fso_list(self, fso_list, metas, show_hidden, selected=None):
        """
        Iterate over the passed in fso objects, collect and return only those
        that should be visible, while attaching the found metadata to each
        object.
        """
        filtered = []
        found_selected = None
        for fso in fso_list:
            # ignore hidden entries if requested
            if not show_hidden and self._is_hidden(fso):
                continue
            # assign extra data to fso objects
            try:
                fso.meta = metas[fso.rel_path]
            except KeyError:
                # ignore entries that have no found facet since they probably
                # do not belong to the requested content type
                continue
            else:
                filtered.append(fso)
                # if selected fso was requested and is matched, remember it
                if selected and fso.name == selected:
                    found_selected = fso
        return (filtered, found_selected)

    def _prepare_listing(self, path, dirs, files, **extra):
        """
        Add meta entries to each file system object and filter those out
        which shouldn't be visible. If ``metas`` was not passed in,  or there
        are paths missing from it, fetch the data in place. If ``content_type``
        is specified, entries that do not belong to a specific content type
        will be ignored.
        """
        metas = extra.pop('metas', {})
        content_type = extra.pop('content_type', {})
        fso_paths = set(fso.rel_path for fso in itertools.chain(dirs, files))
        # get set of missing facet paths (paths of file entries that have no
        # facet data in ``facets`` dict)
        missing_meta_paths = fso_paths.difference(metas.keys())
        if missing_meta_paths:
            metas.update(self._archive.get(missing_meta_paths, content_type))
        # path is guaranteed to be valid at this point
        # get parent folder information (pointed at by ``path``)
        (_, current) = self._fsal.get_fso(path or '.')
        refresh = metas if extra.pop('force_refresh', False) else False
        current.meta = self._archive.parent(path, refresh)
        show_hidden = extra.pop('show_hidden', False)
        selected = extra.pop('selected', None)
        (dirs, selected_dir) = self._filter_fso_list(dirs,
                                                     metas,
                                                     show_hidden,
                                                     selected)
        (files, selected_file) = self._filter_fso_list(files,
                                                       metas,
                                                       show_hidden,
                                                       selected)
        # pick a selection by giving precedence to files over dirs, and falling
        # back to the first file or first directory if no selection was found
        selected = selected_file or selected_dir
        if not selected and files:
            selected = files[0]
        elif not selected and dirs:
            selected = dirs[0]
        return dict(path=path,
                    dirs=dirs,
                    files=files,
                    current=current,
                    selected=selected,
                    **extra)

    def get(self, path, content_type=None):
        """
        Return a single file system object for the given ``path``.
        """
        (success, fso) = self._fsal.get_fso(path)
        if not success:
            raise self.InvalidQuery(path)
        # post-process single entries the same way as with list or search
        metas = self._archive.get(path, content_type, partial=False)
        (filtered, _) = self._filter_fso_list([fso], metas, True)
        return filtered[0]

    def list(self, path, content_type, show_hidden=False, selected=None):
        """
        Return all direct children of the given ``path``. The operation is
        essentially equal to a regular directory listing.
        """
        # fsal cannot accept empty root
        (success, dirs, files) = self._fsal.list_dir(path or '.')
        if not success:
            raise self.InvalidQuery(path)
        # use the more efficient query method for directory listings
        metas = self._archive.for_parent(path, content_type)
        return self._prepare_listing(path,
                                     dirs,
                                     files,
                                     metas=metas,
                                     content_type=content_type,
                                     selected=selected,
                                     force_refresh=not metas,
                                     show_hidden=show_hidden)

    def descendants(self, path, show_hidden=False, **kwargs):
        """
        Return all file-system entries that are located below the given path,
        i.e. those which are descendants of it from a hierarchical view. If
        the optional ``count`` flag is set, only the number of descendants is
        returned, not the actual listing.
        """
        span = self._config['changelog.span']
        ignored_paths = self._config.get('changelog.ignored_paths', [])
        is_count = kwargs.get('count', False)
        order = None if is_count else '-create_time'
        (success,
         count,
         dirs,
         files) = self._fsal.list_descendants(path or '.',
                                              entry_type=0,
                                              order=order,
                                              span=span,
                                              ignored_paths=ignored_paths,
                                              **kwargs)
        if not success:
            raise self.InvalidQuery(path)
        # check if only the number of descendants was requested
        if is_count:
            return count
        # a complete listing was requested, perform regular post-processing
        return self._prepare_listing(path,
                                     dirs,
                                     files,
                                     show_hidden=show_hidden,
                                     count=count)

    def search(self, query, show_hidden=False, language=None):
        """
        Perform a file-system level search, extended with the results of a
        py:class:`Archive`` and py:class:`DirInfo`` based search. In case the
        ``query`` directly matches a file system path, no extended search will
        be performed, instead it will behave similarly as if a regular
        directory listing was requested.
        """
        (dirs, files, is_match) = self._fsal.search(query)
        path = query if is_match else self.ROOT_PATH
        metas = {}
        if not is_match:
            metas = self._archive.search(query, language=language)
        # in case no match was found, ``metas`` contain search results for a
        # different set of paths than those found in ``dirs`` and ``files``.
        # the difference between them must be compensated for on both sides.
        found_paths = (fso.rel_path for fso in itertools.chain(dirs, files))
        # add dirs and files that were present only in meta search results to
        # the results of the file system level search
        missing = set(metas.keys()).difference(found_paths)
        (_, missing_dirs, missing_files) = self._fsal.filter(missing)
        return self._prepare_listing(path,
                                     dirs + missing_dirs,
                                     files + missing_files,
                                     show_hidden=show_hidden,
                                     metas=metas,
                                     is_match=is_match)

    def isdir(self, path):
        return self._fsal.isdir(path)

    def isfile(self, path):
        return self._fsal.isfile(path)

    def exists(self, path):
        return self._fsal.exists(path)

    def remove(self, path):
        return self._fsal.remove(path)

    def move(self, src, dst):
        return self._fsal.move(src, dst)

    def copy(self, src, dst):
        return self._fsal.copy(src, dst)
