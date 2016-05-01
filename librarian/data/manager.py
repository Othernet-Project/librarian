import mimetypes
import os
import re

from ..core.exts import ext_container as exts
from .dirinfo import DirInfo
from .facets.archive import Archive


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
    abstraction layer, py:class:`Facet` and py:class:`DirInfo` facilities. The
    objects returned through it's API provide convenient access to all the
    queried data appropriately connected together.
    """
    #: Exception classes
    Error = Error
    InvalidQuery = InvalidQuery
    #: Alias for py:attr:`Archive.ROOT_PATH`
    ROOT_PATH = Archive.ROOT_PATH
    #: List of filenames which should be ignored
    IGNORED = (
        DirInfo.FILENAME,
    )
    #: Match any string that starts with a period, or has at least one path
    #: separator followed by a period
    RE_PATH_WITH_HIDDEN = re.compile(r'^(\.|.*{}\.)'.format(os.sep))

    def __init__(self, **kwargs):
        self._fsal = kwargs.get('fsal', exts.fsal)
        self._config = kwargs.get('config', exts.config)
        self._databases = kwargs.get('databases', exts.databases)
        self._archive = Archive(db=self._databases.facets,
                                config=self._config,
                                fsal=self._fsal,
                                tasks=kwargs.get('tasks', exts.tasks))

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

    def _prepare_dirs(self, dirs, dirinfos=None, show_hidden=False):
        """
        Add dirinfo entries to each file system object and filter those out
        that should not be visible. In case ``dirinfos`` was not passed in,
        fetch the data in place.
        """
        if dirinfos is None:
            dirinfos = DirInfo.from_db([fso.rel_path for fso in dirs],
                                       immediate=True)
        # iterate over fso objects, collect and return only those that should
        # be visible
        filtered = []
        for fso in dirs:
            if self._is_hidden(fso):
                continue
            # assign extra data to fso objects
            fso.dirinfo = dirinfos[fso.rel_path]
            filtered.append(fso)
        return filtered

    def _prepare_files(self, files, facets=None, facet_type=None,
                       show_hidden=False):
        """
        Add facet entries to each file system object and filter those out
        which shouldn't be visible or their name is on the py:attr:`IGNORED`
        list. If ``facets`` was not passed in,  or there are paths missing
        from it, fetch the data in place. If ``facet_type`` is specified,
        entries that do not belong to a specific facet type will be ignored.
        """
        facets = facets or {}
        file_paths = set(fso.rel_path for fso in files)
        # get set of missing facet paths (paths of file entries that have no
        # facet data in ``facets`` dict)
        missing_facet_paths = file_paths.difference(facets.keys())
        if missing_facet_paths:
            facets.update(self._archive.get(missing_facet_paths, facet_type))
        # iterate over fso objects, collect and return only those that should
        # be visible
        filtered = []
        for fso in files:
            # ignore entries that do not belong to the specified ``facet_type``
            if fso.rel_path not in facets:
                continue
            # ignore entries that are on the global ignore list, or are hidden
            if fso.name in self.IGNORED or self._is_hidden(fso):
                continue
            # assign extra data to fso objects
            mimetype, encoding = mimetypes.guess_type(fso.rel_path)
            fso.mimetype = mimetype
            fso.facets = facets[fso.rel_path]
            filtered.append(fso)
        return filtered

    def _prepare_listing(self, dirs, files, **extra):
        """
        Wrap the passed in ``dirs`` and ``files`` in their respective iterators
        returning them in a dictionary with all the ``extra`` data included as
        optional keyword arguments and the fetched facet types for the given
        parent `path`.
        """
        # path is guaranteed to be valid at this point
        path = extra.get('path')
        (_, current) = self._fsal.get_fso(path)
        # get parent folder information (pointed at by ``path``)
        current.facets = self._archive.parent(path)
        current.dirinfo = DirInfo.from_db([path], immediate=True).get(path, {})
        show_hidden = extra.pop('show_hidden', False)
        dirs = self._prepare_dirs(dirs,
                                  dirinfos=extra.pop('dirinfos', None),
                                  show_hidden=show_hidden)
        files = self._prepare_files(files,
                                    facets=extra.pop('facets', None),
                                    facet_type=extra.pop('facet_type', None),
                                    show_hidden=show_hidden)
        return dict(dirs=dirs, files=files, current=current, **extra)

    def get(self, path, facet_type=None):
        """
        Return a single file system object for the given ``path``.
        """
        (success, fso) = self._fsal.get_fso(path)
        if not success:
            raise self.InvalidQuery(path)
        # post-process single entries the same way as with list or search
        if fso.is_dir():
            (fso,) = self._prepare_dirs([fso])
        else:
            (fso,) = self._prepare_files([fso], facet_type=facet_type)
        return fso

    def list(self, path, facet_type, show_hidden=False):
        """
        Return all direct children of the given ``path``. The operation is
        essentially equal to a regular directory listing.
        """
        (success, dirs, files) = self._fsal.list_dir(path)
        if not success:
            raise self.InvalidQuery(path)
        # use the more efficient query method for directory listings
        facets = self._archive.for_parent(path, facet_type)
        return self._prepare_listing(dirs,
                                     files,
                                     facets=facets,
                                     facet_type=facet_type,
                                     show_hidden=show_hidden,
                                     path=path)

    def descendants(self, path, show_hidden=False, **kwargs):
        """
        Return all file-system entries that are located below the given path,
        i.e. those which are descendants of it from a hierarchical view. If
        the optional ``count`` flag is set, only the number of descendants is
        returned, not the actual listing.
        """
        span = self._config['changelog.span']
        ignored_paths = self._config.get('changelog.ignored_paths', [])
        (success,
         count,
         dirs,
         files) = self._fsal.list_descendants(path,
                                              entry_type=0,
                                              order='-create_time',
                                              span=span,
                                              ignored_paths=ignored_paths,
                                              **kwargs)
        if not success:
            raise self.InvalidQuery(path)
        # check if only the number of descendants was requested
        if kwargs.get('count', False):
            return count
        # a complete listing was requested, perform regular post-processing
        return self._prepare_listing(dirs,
                                     files,
                                     show_hidden=show_hidden,
                                     path=path,
                                     count=count)

    def search(self, query, show_hidden=False, **kwargs):
        """
        Perform a file-system level search, extended with the results of a
        py:class:`Archive`` and py:class:`DirInfo`` based search. In case the
        ``query`` directly matches a file system path, no extended search will
        be performed, instead it will behave similarly as if a regular
        directory listing was requested.
        """
        path = query
        (dirs, files, is_match) = self._fsal.search(query)
        facets = {}
        dirinfos = {}
        if not is_match:
            path = self.ROOT_PATH
            facets = self._archive.search(query)
            dirinfos = DirInfo.search(terms=query,
                                      language=kwargs.get('language'))
        # in case no match was found, both ``facets`` and ``dirinfos`` contain
        # search results for a different set of paths than those found in
        # ``dirs`` and ``files``. the difference between them must be
        # compensated for on both sides.
        dir_paths = set(fso.rel_path for fso in dirs)
        file_paths = set(fso.rel_path for fso in files)
        dirinfo_paths = set(dirinfos.keys())
        facet_paths = set(facets.keys())
        # merge missing dirinfo data into the dirinfo search results
        dirinfos.update(DirInfo.from_db(dir_paths.difference(dirinfo_paths),
                                        immediate=True))
        # add dirs and files that were present only in dirinfo and facet
        # search results to the results of the file system level search
        missing = (list(dirinfo_paths.difference(dir_paths)) +
                   list(facet_paths.difference(file_paths)))
        (success, missing_dirs, missing_files) = self._fsal.filter(missing)
        return self._prepare_listing(dirs + missing_dirs,
                                     files + missing_files,
                                     show_hidden=show_hidden,
                                     dirinfos=dirinfos,
                                     facets=facets,
                                     path=path,
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
