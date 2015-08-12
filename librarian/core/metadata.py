"""
metadata.py: Handling metadata

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

import os
import json
import functools

import scandir

from outernet_metadata import validator


CONTENT_TYPES = {
    'generic': 1,
    'html': 2,
    'video': 4,
    'audio': 8,
    'app': 16,
    'image': 32,
}
ALIASES = {
    'publisher': ['partner'],
}


def is_deprecated(key):
    return validator.values.v.deprecated in validator.values.SPECS[key]


def get_edge_keys():
    """ Return the most recent valid key names.

    :returns:  tuple of strings(key names)"""
    edge_keys = set()
    for key in validator.values.KEYS:
        if not is_deprecated(key):
            edge_keys.add(key)

    return tuple(edge_keys)


EDGE_KEYS = get_edge_keys()


class MetadataError(Exception):
    """ Base metadata error """
    def __init__(self, msg, errors):
        self.errors = errors
        super(MetadataError, self).__init__(msg)


def add_missing_keys(meta):
    """ Make sure metadata dict contains all keys defined in the specification,
    using the default values from the specification itself for missing keys.

    This function modifies the metadata dict in-place, and has no useful return
    value.

    :param meta:    metadata dict
    """
    for key in EDGE_KEYS:
        if key not in meta:
            meta[key] = validator.values.DEFAULTS.get(key, None)


def replace_aliases(meta):
    """ Replace deprecated aliases with their current substitution.

    This function modifies the metadata dict in-place, and has no useful return
    value.

    :param meta:    metadata dict
    """
    for key in EDGE_KEYS:
        if key not in meta:
            for alias in ALIASES.get(key, []):
                if alias in meta:
                    meta[key] = meta.pop(alias)


def clean_keys(meta):
    """ Make sure metadta dict does not have any non-standard keys

    This function modifies the metadata dict in-place, and always returns
    ``None``.

    :param meta:  metadata dict
    """
    for key in meta.keys():
        if key not in EDGE_KEYS:
            del meta[key]


def process_meta(meta):
    failed = validator.validate(meta, broadcast=True)
    if failed:
        keys = ', '.join(failed.keys())
        msg = "Metadata validation failed for keys: {0}".format(keys)
        raise MetadataError(msg, failed)

    replace_aliases(meta)
    add_missing_keys(meta)
    clean_keys(meta)
    return meta


def determine_content_type(meta):
    """Calculate bitmask of the passed in metadata based on the content types
    found in it."""
    calc = lambda mask, key: mask + CONTENT_TYPES.get(key.lower(), 0)
    return functools.reduce(calc, meta['content'].keys(), 0)


class Meta(object):
    """ Metadata wrapper with additional methods for easier consumption

    This classed is used as a dict wrapper that provides attrbute access to
    keys, and a few additional properties and methods to ease working with
    metadta.

    Parts of this class are tied to the filesystem (notably the parts that deal
    with content thumbnails). This functionality may be factored out of this
    class at a later time.
    """
    def __init__(self, meta, content_path):
        """ Metadata wrapper instantiation

        :param meta:          dict: Raw metadata as dict
        :param content_path:  str: Absolute path to specific content
        """
        self.meta = dict((key, meta[key]) for key in meta.keys())
        # We use ``or`` in the following line because 'tags' can be an empty
        # string, which is treated as invalid JSON
        self.tags = json.loads(meta.get('tags') or '{}')
        self._files = None
        self.content_path = content_path

    def __getattr__(self, attr):
        try:
            return self.meta[attr]
        except KeyError:
            raise AttributeError("Attribute or key '%s' not found" % attr)

    def __getitem__(self, key):
        return self.meta[key]

    def __setitem__(self, key, value):
        self.meta[key] = value

    def __delitem__(self, key):
        del self.meta[key]

    def __contains__(self, key):
        return key in self.meta

    def get(self, key, default=None):
        """ Return the value of a metadata or the default value

        This method works exactly the same as ``dict.get()``, except that it
        only works on the keys that exist on the underlying metadata dict.

        :param key:     name of the key to look up
        :param default: default value to use if key is missing
        """
        return self.meta.get(key, default)

    def find_files(self):
        if not self.content_path or not os.path.exists(self.content_path):
            return []

        return [(filename, os.stat(os.path.join(root, filename)).st_size)
                for root, _, filenames in scandir.walk(self.content_path)
                for filename in filenames
                if filename != 'info.json']

    @property
    def lang(self):
        return self.meta.get('language')

    @property
    def label(self):
        if self.meta.get('archive') == 'core':
            return 'core'
        elif self.meta.get('is_sponsored'):
            return 'sponsored'
        elif self.meta.get('is_partner'):
            return 'partner'
        return 'core'

    @property
    def files(self):
        if self._files is None:
            self._files = self.find_files()
        return self._files

    @property
    def content_type_names(self):
        """Return list of content type names present in a content object."""
        return [name for (name, cid) in CONTENT_TYPES.items()
                if self.meta['content_type'] & cid == cid]
