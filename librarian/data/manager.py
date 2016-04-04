import os
import re
import mimetypes
from itertools import izip_longest

from bottle import request
from bottle_utils.common import to_unicode

from librarian_content.facets.utils import (
    get_facets, get_dir_facets, get_archive)

from .dirinfo import DirInfo


# Match any string that starts with a period, or has at least one path
# separator followed by a period
RE_PATH_WITH_HIDDEN = re.compile(r'^(\.|.*{}\.)'.format(os.sep))


def nohidden(fsos):
    for fso in fsos:
        if not RE_PATH_WITH_HIDDEN.match(fso.rel_path):
            yield fso


def unique_results(*iterables):
    results = set()
    for it in iterables:
        results |= set(it)
    return list(results)


class Manager(object):

    META_FILES = DirInfo.FILENAME

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.fsal_client = self.supervisor.exts.fsal
        self.config = supervisor.config

    def get_dirinfos(self, paths):
        return DirInfo.from_db(self.supervisor, paths, immediate=True)

    def get_facets(self, files):
        return get_facets(f.rel_path for f in files)

    def get_dir_facets(self, path, files):
        return get_dir_facets(path, (f.name for f in files))

    def _extend_dirs(self, dirs):
        plain_dirs = [fso for fso in dirs if not hasattr(fso, 'dirinfo')]
        dirpaths = [fs_obj.rel_path for fs_obj in plain_dirs]
        dirinfos = self.get_dirinfos(dirpaths)
        for fs_obj in plain_dirs:
            fs_obj.dirinfo = dirinfos[fs_obj.rel_path]
        return dirs

    def _extend_file(self, fs_obj):
        mimetype, encoding = mimetypes.guess_type(fs_obj.rel_path)
        fs_obj.mimetype = mimetype
        fs_obj.parent = to_unicode(
            os.path.basename(os.path.dirname(fs_obj.rel_path)))
        return fs_obj

    def _extend_files(self, files, limit=None):
        """
        Extend files with facet data. The optional ``limit`` argument is a
        directory path, which changes the way facets are looked up. When
        ``limit`` is specified, facets are looked up by directory path, rather
        than full path, which speeds the query up.
        """
        plain_files = [fso for fso in files if not hasattr(fso, 'facets')]
        if limit:
            facets = self.get_dir_facets(limit, plain_files)
        else:
            facets = self.get_facets(plain_files)
        for f, facets in izip_longest(plain_files, facets):
            f.facets = facets
        return files

    def _process_listing(self, dirs, unfiltered_files, limit=None):
        dirs = list(dirs)
        unfiltered_files = list(unfiltered_files)
        meta = {}
        files = []
        self._extend_dirs(dirs)
        for fs_obj in unfiltered_files:
            self._extend_file(fs_obj)
            if fs_obj.name == self.META_FILES:
                meta[fs_obj.name] = fs_obj
            else:
                files.append(fs_obj)
        return (dirs, self._extend_files(files, limit), meta)

    def get(self, path):
        success, fso = self.fsal_client.get_fso(path)
        if not success:
            return None
        if fso.is_dir():
            self._extend_dirs([fso])
        else:
            self._extend_file(fso)
        return fso

    def list(self, path, show_hidden=False):
        (success, dirs, files) = self.fsal_client.list_dir(path)
        if not show_hidden:
            dirs = nohidden(dirs)
            files = nohidden(files)
        (dirs, files, meta) = self._process_listing(dirs, files, limit=path)
        return (success, dirs, files, meta)

    def list_descendants(self, path, show_hidden=False, **kwargs):
        kwargs.setdefault('ignored_paths', []).extend(
            self.config.get('changelog.ignored_paths', []))
        (success,
         count,
         dirs,
         files) = self.fsal_client.list_descendants(path, **kwargs)
        if not show_hidden:
            dirs = nohidden(dirs)
            files = nohidden(files)

        (dirs, files, meta) = self._process_listing(dirs, files)
        return (success, count, dirs, files, meta)

    def search(self, query, show_hidden=False):
        (dirs, files, is_match) = self.fsal_client.search(query)
        if not is_match:
            facets_results = self.search_facets(query)
            dirinfo_results = self.search_dirinfos(query)
            files = unique_results(files, facets_results)
            dirs = unique_results(dirs, dirinfo_results)
        if not show_hidden:
            dirs = nohidden(dirs)
            files = nohidden(files)
        (dirs, files, meta) = self._process_listing(dirs, files)
        return (dirs, files, meta, is_match)

    def search_facets(self, query, facet_type=None):
        facets = get_archive().search(query, facet_type=facet_type)
        files = []
        for f in facets:
            path = os.path.join(f['path'], f['file'])
            success, fso = self.fsal_client.get_fso(path)
            if not success:
                continue
            fso.facets = f
            files.append(fso)
        return files

    def search_dirinfos(self, query):
        default_lang = request.user.options.get('content_language', None)
        lang = request.params.get('language', default_lang)
        dirinfos = DirInfo.search(
            self.supervisor, terms=query, language=lang)
        dirs = []
        for d in dirinfos:
            success, fso = self.fsal_client.get_fso(d.path)
            if not success:
                continue
            fso.dirinfo = d
            dirs.append(fso)
        return dirs

    def isdir(self, path):
        return self.fsal_client.isdir(path)

    def isfile(self, path):
        return self.fsal_client.isfile(path)

    def exists(self, path):
        return self.fsal_client.exists(path)

    def remove(self, path):
        return self.fsal_client.remove(path)

    def move(self, src, dst):
        return self.fsal_client.move(src, dst)

    def copy(self, src, dst):
        return self.fsal_client.copy(src, dst)
