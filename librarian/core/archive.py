"""
archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import logging
import os
import shutil

from .downloads import (get_spool_zip_path,
                        get_zip_path,
                        get_metadata,
                        get_md5_from_path)
from .metadata import clean_keys


FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}


def parse_size(size):
    """ Parses size with B, K, M, or G suffix and returns in size bytes

    :param size:    human-readable size with suffix
    :returns:       size in bytes or 0 if source string is using invalid
                    notation
    """
    size = size.strip().lower()
    if size[-1] not in 'bkmg':
        suffix = 'b'
    else:
        suffix = size[-1]
        size = size[:-1]
    try:
        size = float(size)
    except ValueError:
        return 0
    return size * FACTORS[suffix]


class Archive(object):

    def __init__(self, backend):
        name = BaseArchive.__name__

        if not isinstance(backend, BaseArchive):
            raise TypeError('arg 1 must be an instance of {0}'.format(name))

        if not hasattr(backend, '_{0}__initialized'.format(name)):
            msg = ("{0} not initialized. Make sure the __init__ function of "
                   "the superclass is invoked.".format(name))
            raise RuntimeError(msg)

        object.__setattr__(self, 'backend', backend)

    def __getattribute__(self, name):
        backend = object.__getattribute__(self, 'backend')
        return getattr(backend, name)

    def __setattr__(self, name, value):
        backend = object.__getattribute__(self, 'backend')
        setattr(backend, name, value)

    @staticmethod
    def get_backend_class(backend_path):
        splitted = backend_path.split('.')
        backend_cls_name = splitted[-1]
        try:
            # try loading from pythonpath
            mod = __import__(backend_path, fromlist=[backend_cls_name])
        except ImportError:
            # backend not on pythonpath, try loading it from local package
            from . import backends
            backend_path = '.'.join([backends.__name__] + splitted[:-1])
            mod = __import__(backend_path, fromlist=[backend_cls_name])

        return getattr(mod, backend_cls_name)

    @classmethod
    def setup(cls, backend_path, *args, **kwargs):
        backend_cls = cls.get_backend_class(backend_path)
        backend = backend_cls(*args, **kwargs)
        return cls(backend)


class BaseArchive(object):

    required_config_params = (
        'contentdir',
        'spooldir',
        'meta_filename',
    )

    def __init__(self, **config):
        self.config = config
        for key in self.required_config_params:
            if key not in self.config:
                raise TypeError("{0}.__init__() needs keyword-only argument "
                                "{1}".format(type(self).__name__, key))

        self.__initialized = True

    def get_count(self, tag=None, lang=None, multipage=None):
        raise NotImplementedError()

    def get_content(self, terms=None, offset=0, limit=0, tag=None, lang=None,
                    multipage=None):
        raise NotImplementedError()

    def get_single(self, md5):
        raise NotImplementedError()

    def get_titles(self, ids):
        raise NotImplementedError()

    def get_replacements(self, metadata):
        replacements = []
        for m in metadata:
            if m.get('replaces') is not None:
                replacements.append(m['replaces'])

        if replacements:
            titles = self.get_titles(replacements)
        else:
            return []

        titles = {m['md5']: m['title'] for m in titles}
        for m in metadata:
            if m.get('replaces') in titles:
                m['replaces_title'] = titles[m['replaces']]

        return metadata

    def content_for_domain(self, domain):
        raise NotImplementedError()

    def prepare_metadata(self, md5, path):
        meta = get_metadata(path, self.config['meta_filename'])
        clean_keys(meta)
        meta['md5'] = md5
        meta['updated'] = datetime.datetime.now()
        meta['size'] = os.stat(path).st_size
        return meta

    def add_meta_to_db(self, metadata, replaced):
        raise NotImplementedError()

    def remove_meta_from_db(self, hashes):
        raise NotImplementedError()

    def delete_obsolete(self, obsolete):
        for path in obsolete:
            if not path:
                continue

            try:
                os.unlink(path)
            except OSError as err:
                logging.error(
                    "<%s> could not delete obsolete file: %s" % (path, err))

    def copy_to_archive(self, paths, target_dir):
        for path in paths:
            target_path = os.path.join(target_dir, os.path.basename(path))
            if os.path.exists(target_path):
                logging.debug("<%s> removing existing content" % target_path)
                os.unlink(target_path)

            shutil.move(path, target_dir)

    def process_content_files(self, content):
        to_add = []
        to_replace = []
        to_copy = []
        to_delete = []
        # Prepare data for processing
        for md5, path in content:
            if not path:
                logging.debug("skipping '%s', file not found", md5)
                continue

            logging.debug("<%s> adding to archive (#%s)" % (path, md5))
            meta = self.prepare_metadata(md5, path)
            if meta.get('replaces'):
                logging.debug("<%s> replaces '%s'" % (path, meta['replaces']))
                to_replace.append(meta['replaces'])
                to_delete.append(get_zip_path(meta['replaces'],
                                              self.config['contentdir']))

            to_copy.append(path)
            to_add.append(meta)

        return to_add, to_replace, to_delete, to_copy

    def process_content(self, to_add, to_replace, to_delete, to_copy):
        rowcount = self.add_meta_to_db(to_add, to_replace)
        self.delete_obsolete(to_delete)
        self.copy_to_archive(to_copy, self.config['contentdir'])
        return rowcount

    def process(self, content, no_file_ops=False):
        (to_add,
         to_replace,
         to_delete,
         to_copy) = self.process_content_files(content)

        if no_file_ops:
            to_delete = []
            to_copy = []

        rows = self.process_content(to_add, to_replace, to_delete, to_copy)
        return rows, len(to_delete), len(to_copy)

    def add_to_archive(self, hashes):
        spooldir = self.config['spooldir']
        content = ((h, get_spool_zip_path(h, spooldir)) for h in hashes)
        rows, deleted, copied = self.process(content)
        logging.debug("%s items added to database", rows)
        logging.debug("%s items deleted from storage", deleted)
        logging.debug("%s items copied to storage", copied)
        return rows

    def remove_from_archive(self, hashes):
        failed = []
        contentdir = self.config['contentdir']
        for md5, path in ((h, get_zip_path(h, contentdir)) for h in hashes):
            logging.debug("<%s> removing from archive (#%s)" % (path, md5))
            if path is None:
                failed.append(md5)
                continue

            try:
                os.unlink(path)
            except OSError as err:
                logging.error("<%s> cannot delete: %s" % (path, err))
                failed.append(md5)
                continue

        rowcount = self.remove_meta_from_db(hashes)
        logging.debug("%s items removed from database" % rowcount)
        return failed

    def reload_data(self):
        contentdir = self.config['contentdir']
        content = ((get_md5_from_path(f), os.path.join(contentdir, f))
                   for f in os.listdir(contentdir)
                   if f.endswith('.zip'))
        res = self.process(content, no_file_ops=True)
        return res[0]

    def clear_and_reload(self):
        raise NotImplementedError()

    def last_update(self):
        raise NotImplementedError()

    def add_view(self, md5):
        raise NotImplementedError()

    def add_tags(self, meta, tags):
        raise NotImplementedError()

    def remove_tags(self, meta, tags):
        raise NotImplementedError()

    def get_tag_name(self, tag_id):
        raise NotImplementedError()

    def get_tag_cloud(self):
        raise NotImplementedError()

    def needs_formatting(self, md5):
        raise NotImplementedError()
