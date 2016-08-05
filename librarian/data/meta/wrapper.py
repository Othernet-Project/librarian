"""
Wrapper for metadata entries queried from meta archive.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import os

from .contenttypes import ContentTypes
from .metadata import NO_LANGUAGE


class MetaWrapper(object):
    """
    Lightweight wrapper object around content metadata.
    """
    #: Cached `key:type_caster_function` mapping for faster access
    CASTERS = ContentTypes.keys()

    def __init__(self, data):
        self._data = data
        self._metadata = self._data.get('metadata', {})

    def get(self, key, language=NO_LANGUAGE, default=None):
        """
        Return ``key`` from internal data structure holding the metadata.

        If ``language`` is specified, attempt retrieving the data under that
        specifiec language, and fall back to language-less version of the data
        if not found. In case both previous lookups failed, ``default`` is
        returned.
        """
        caster_fn = self.CASTERS.get(key, lambda x: x)
        try:
            # lookup under specific language / key
            return caster_fn(self._metadata[language][key])
        except KeyError:
            try:
                # specific language not found, try language-less version
                return caster_fn(self._metadata[NO_LANGUAGE][key])
            except KeyError:
                # return default value since no data was found under given keys
                return default

    @property
    def path(self):
        """
        Return ``path`` of file system object to which the metadata belongs.
        """
        return self._data['path']

    @property
    def name(self):
        """
        Return the name of the file system object, without path.
        """
        return os.path.basename(self.path)

    @property
    def type(self):
        """
        Return the type of the file system object (whether it's a file or
        directory).
        """
        return self._data['type']

    @property
    def mime_type(self):
        """
        Return the detected mime type for the file system object.
        """
        return self._data['mime_type']

    @property
    def content_types(self):
        """
        Return bitmask of detected content types for the file system object.
        """
        return self._data['content_types']

    @property
    def content_type_names(self):
        """
        Return a list of detected content types for the file system object.
        """
        return ContentTypes.from_bitmask(self.content_types)

    def unwrap(self):
        """
        Return the internal data structure.
        """
        return self._data

    def has_key(self, key):
        """
        Return whether the current object's content types support ``key``.
        """
        return any(key in ContentTypes.keys(content_type)
                   for content_type in self.content_type_names)
