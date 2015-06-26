"""
archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import functools
import logging
import os
import shutil

from . import content
from . import metadata
from . import zipballs


def is_string(obj):
    if 'basestring' not in globals():
        basestring = str
    return isinstance(obj, basestring)


def content_id_list(func):
    """In case a single content id string is passed to the function wrapped
    with this decorator, the content id string will be wrapped in a list."""
    @functools.wraps(func)
    def wrapper(self, content_ids):
        if is_string(content_ids):
            content_ids = [content_ids]
        return func(self, content_ids)
    return wrapper


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
        'unpackdir',
        'contentdir',
        'spooldir',
        'meta_filename',
    )
    meta_db_mapping = {
        'replaces': None,
        'index': 'entry_point'
    }
    db_fields = (
        'md5',
        'size',
        'updated',
    ) + tuple(filter(None, [meta_db_mapping.get(key, key)
                            for key in metadata.EDGE_KEYS]))

    def __init__(self, **config):
        self.config = config
        for key in self.required_config_params:
            if key not in self.config:
                raise TypeError("{0}.__init__() needs keyword-only argument "
                                "{1}".format(type(self).__name__, key))

        self.__initialized = True

    def get_count(self, terms=None, tag=None, lang=None, multipage=None):
        """Return the number of matching content metadata filtered by the given
        options.
        Implementation is backend specific.

        :param terms:      string: search query
        :param tag:        list of string tags
        :param lang:       string: language code
        :param multipage:  bool"""
        raise NotImplementedError()

    def get_content(self, terms=None, offset=0, limit=0, tag=None, lang=None,
                    multipage=None):
        """Return iterable of matching content metadata filtered by the given
        options.
        Implementation is backend specific.

        :param terms:      string: search query
        :param offset:     int: start index
        :param limit:      int: max number of items to be returned
        :param tag:        list of string tags
        :param lang:       string: language code
        :param multipage:  bool"""
        raise NotImplementedError()

    def get_single(self, content_id):
        """Return a single metadata object matching the given content id.
        Implementation is backend specific.

        :param content_id:  ID of content"""
        raise NotImplementedError()

    def get_multiple(self, content_ids, fields=None):
        """Return iterable of matching content metadatas by the given list of
        content ids.
        Implementation is backend specific.

        :param content_ids:  iterable of content ids to be found
        :param fields:       list of fields to be fetched (defaults to all)"""
        raise NotImplementedError()

    def content_for_domain(self, domain):
        """Return iterable of content metadata partially matching the specified
        domain.
        Implementation is backend specific.

        :param domain:  string
        :returns:       iterable of matched contents"""
        raise NotImplementedError()

    def add_meta_to_db(self, meta):
        """Add the passed in content metadata to the database.
        Implementation is backend specific.

        :param metadata:  Dictionary of valid content metadata"""
        raise NotImplementedError()

    def remove_meta_from_db(self, content_id):
        """Remove the specified content's metadata from the database.
        Implementation is backend specific.

        :param content_id:  Id of content that is about to be deleted"""
        raise NotImplementedError()

    def add_replacement_data(self, metas, needed_keys, key_prefix='replaces_'):
        """Modify inplace the list of passed in metadata dicts by adding the
        needed data about the content that is about to be replaced to the new
        meta information, with it's keys prefixed by the specified string.
        [{
            'md5': '123',
            'title': 'first',
            'replaces': '456',
            ...
        }, {
            'md5': 'abc',
            'title': 'second',
            ...
        }]

        Will be turned into:

        [{
            'md5': '123',
            'title': 'first',
            'replaces': '456',
            'replaces_title': 'old content title',
             ...
        }, {
            'md5': 'abc',
            'title': 'second',
            ...
        }]
        """
        replaceable_ids = [meta['replaces'] for meta in metas
                           if meta.get('replaces') is not None]
        if not replaceable_ids:
            return

        needed_fields = tuple(sorted(set(tuple(needed_keys) + ('md5',))))
        replaceables = self.get_multiple(replaceable_ids, fields=needed_fields)
        get_needed_data = lambda d: dict((key, d[key]) for key in needed_keys)
        replaceable_metas = dict((data['md5'], get_needed_data(data))
                                 for data in replaceables)
        for meta in metas:
            if meta.get('replaces') in replaceable_metas:
                replaceable_metadata = replaceable_metas[meta['replaces']]
                for key in needed_keys:
                    replace_key = '{0}{1}'.format(key_prefix, key)
                    meta[replace_key] = replaceable_metadata[key]

    def delete_content_files(self, content_id):
        """Delete the specified content's directory and all of it's files.

        :param content_id:  Id of content that is about to be deleted
        :returns:           bool: indicating success of deletion"""
        content_path = content.to_path(content_id,
                                       prefix=self.config['contentdir'])
        if not content_path:
            msg = "Invalid content_id passed: '{0}'".format(content_id)
            logging.debug(msg)
            return False

        try:
            shutil.rmtree(content_path)
        except Exception as exc:
            logging.debug("Deletion of '{0}' failed: '{1}'".format(content_id,
                                                                   exc))
            return False
        else:
            return True

    def __add_auto_fields(self, meta, contentdir, content_id):
        # add auto-generated values to metadata before writing into db
        meta['md5'] = content_id
        meta['updated'] = datetime.datetime.now()
        meta['size'] = content.get_content_size(contentdir, content_id)

    def extract_zipball(self, zip_path, contentdir):
        """Extract zipball found on `zip_path` into `contentdir`.
        Before content extraction begins, symlink the extractedable zipball
        into `unpackdir`, and remove the symlink only if extraction was
        successful.
        Startup hooks will look for symlinks that were not removed, which means
        a zipball extraction failed and will attempt to resolve the issue."""
        filename = os.path.basename(zip_path)
        symlink_path = os.path.join(self.config['unpackdir'], filename)
        if not os.path.exists(symlink_path):
            os.symlink(zip_path, symlink_path)

        zipballs.extract(zip_path, contentdir)
        # if extract didn't raise an exception, it's safe to remove the symlink
        os.unlink(symlink_path)

    def process_content(self, content_id, zip_path, meta):
        """Extract zipball and add it's metadata to the database.
        - If extraction fails, it deletes the content folder.
        - If metadata specifies that content is a replacement, old content will
          be removed accordingly and replaced by new one.

        :param content_id:  Id of content
        :param zip_path:    Path to zipball to be extracted
        :param meta:        Dictionary containing valid and clean metadata
        :returns:           int / bool: indicating success
        """
        contentdir = self.config['contentdir']
        try:
            self.extract_zipball(zip_path, contentdir)
        except Exception as exc:
            logging.debug("Extraction of '{0}' failed: "
                          "'{1}'".format(zip_path, exc))
            self.delete_content_files(content_id)
            return False
        else:
            # extraction successful, delete zipball
            os.remove(zip_path)
            self.__add_auto_fields(meta, contentdir, content_id)
            return self.add_meta_to_db(meta)

    def __add_to_archive(self, content_id, src_dir):
        # Validate specified zipball found in `src_dir` by it's `content_id`
        # extract it and add it to archive database.
        logging.debug("Adding content '{0}' to archive.".format(content_id))
        meta_filename = self.config['meta_filename']
        zip_path = zipballs.get_zip_path(content_id, src_dir)
        try:
            meta = zipballs.validate(zip_path, meta_filename=meta_filename)
        except zipballs.ValidationError as exc:
            logging.debug("Validation of '{0}' failed: "
                          "'{1}'".format(zip_path, exc))
            return False
        else:
            return self.process_content(content_id, zip_path, meta)

    @content_id_list
    def add_to_archive(self, content_ids):
        """Add the specified newly downloaded content(s) to the library.
        Unpacks zipballs located in `spooldir` into `contentdir` and adds their
        meta information to the database. The zipball from `spooldir` will be
        deleted on successful import.

        :param content_ids:  string: a single content id to be added
                             iterable: an iterable of content ids to be added
        :returns:            int: successfully added content count
        """
        return sum([self.__add_to_archive(cid, self.config['spooldir'])
                    for cid in content_ids])

    def __remove_from_archive(self, content_id):
        msg = "Removing content '{0}' from archive.".format(content_id)
        logging.debug(msg)
        self.delete_content_files(content_id)
        return self.remove_meta_from_db(content_id)

    @content_id_list
    def remove_from_archive(self, content_ids):
        """Removes the specified content(s) from the library.
        Deletes the matching content files from `contentdir` and removes their
        meta information from the database.

        :param content_ids:  string: a single content id to be removed
                             iterable: an iterable of content ids to be removed
        :returns:            int: successfully removed content count"""
        return sum([self.__remove_from_archive(cid) for cid in content_ids])

    def __reload_content(self, content_id, contentdir):
        meta_filename = self.config['meta_filename']
        try:
            raw_meta = content.get_meta(contentdir, content_id, meta_filename)
            meta = metadata.process_meta(raw_meta)
        except metadata.MetadataError as exc:
            logging.debug("Metadata of '{0}' is invalid: "
                          "'{1}'".format(content_id, exc))
            return False
        except (OSError, IOError) as exc:
            logging.debug("Error opening metadata: '{1}'".format(content_id,
                                                                 exc))
            return False
        else:
            self.__add_auto_fields(meta, contentdir, content_id)
            return self.add_meta_to_db(meta)

    def reload_content(self):
        """Reload all existing content from `contentdir` into database."""
        contentdir = self.config['contentdir']
        cont_ids = [content.to_md5(os.path.relpath(content_path, contentdir))
                    for content_path in content.find_content_dirs(contentdir)]
        return sum([self.__reload_content(cid, contentdir)
                    for cid in cont_ids if cid])

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

    def get_content_languages(self):
        raise NotImplementedError()
