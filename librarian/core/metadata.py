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

import scandir

from outernet_metadata import validator


ALIASES = {
    'publisher': ['partner'],
    'entry_point': ['index']
}


def get_successor_key(key):
    """ If a key becomes obsolete, return it's successor.

    :param key:  string: old(now obsolete) key name
    :returns:    string: new(successor) key name"""
    for edge_key, edge_aliases in ALIASES.items():
        for obsolete_key in edge_aliases:
            if obsolete_key == key:
                return edge_key


def get_edge_keys():
    """ Return the most recent valid key names.

    :returns:  tuple of strings(key names)"""
    edge_keys = set()
    for key in validator.values.KEYS:
        successor = get_successor_key(key)
        edge_keys.add(successor or key)

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
            # entry_point is not a valid key by specification, but is used
            # by librarian nevertheless to avoid conflicts with SQL
            def_key = 'index' if key == 'entry_point' else key
            meta[key] = validator.values.DEFAULTS.get(def_key, None)


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
    failed.pop('broadcast', None)  # TODO: remove this after until v0.3
    if failed:
        keys = ', '.join(failed.keys())
        msg = "Metadata validation failed for keys: {0}".format(keys)
        raise MetadataError(msg, failed)

    replace_aliases(meta)
    add_missing_keys(meta)
    clean_keys(meta)
    return meta


class Meta(object):
    """ Metadata wrapper with additional methods for easier consumption

    This classed is used as a dict wrapper that provides attrbute access to
    keys, and a few additional properties and methods to ease working with
    metadta.

    Parts of this class are tied to the filesystem (notably the parts that deal
    with content thumbnails). This functionality may be factored out of this
    class at a later time.
    """

    IMAGE_EXTENSIONS = ('.png', '.gif', '.jpg', '.jpeg')

    def __init__(self, meta, content_path):
        """ Metadata wrapper instantiation

        :param meta:          dict: Raw metadata as dict
        :param content_path:  str: Absolute path to specific content
        """
        self.meta = dict((key, meta[key]) for key in meta.keys())
        # We use ``or`` in the following line because 'tags' can be an empty
        # string, which is treated as invalid JSON
        self.tags = json.loads(meta.get('tags') or '{}')
        self._image = None
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

    def find_image(self):
        if not self.content_path or not os.path.exists(self.content_path):
            return None

        for entry in scandir.scandir(self.content_path):
            extension = os.path.splitext(entry.name)[1].lower()
            if extension in self.IMAGE_EXTENSIONS:
                return entry.name

        return None

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
    def image(self):
        if self._image is not None:
            return self._image

        self._image = self.find_image()
        return self._image
