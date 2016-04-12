"""
facets.py: Handling metadata

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from .base import CDFObject


class FacetTypes:
    # Special purpose-meta types
    UPDATES = 'updates'
    # Actual facet types
    GENERIC = 'generic'
    HTML = 'html'
    VIDEO = 'video'
    AUDIO = 'audio'
    IMAGE = 'image'
    MAPPING = {
        GENERIC: 1,
        HTML: 2,
        VIDEO: 4,
        AUDIO: 8,
        IMAGE: 16,
    }

    @classmethod
    def bitmask(cls, name):
        return cls.MAPPING[name]

    @classmethod
    def is_valid(cls, name):
        return name in cls.MAPPING

    @classmethod
    def names(cls):
        return cls.MAPPING.keys()


FACET_TYPES = FacetTypes.MAPPING  # For backwards compatibility


class Facets(CDFObject):
    DATABASE_NAME = 'facets'
    TABLE_NAME = 'facets'
    CACHE_KEY_TEMPLATE = u'facets_{0}'
    ATTEMPT_READ_FROM_FILE = False
    ALLOW_EMPTY_INSTANCES = False

    def __init__(self, *args, **kwargs):
        super(Facets, self).__init__(*args, **kwargs)

    def __getattr__(self, attr):
        try:
            return self._data[attr]
        except KeyError:
            raise AttributeError("Attribute or key '%s' not found" % attr)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def update(self, other):
        if isinstance(other, dict):
            self._data.update(other)
        elif isinstance(other, Facets):
            self._data.update(other._data)
        else:
            raise RuntimeError(
                "Cannot update with type {}".format(type(other)))

    def has_type(self, facet_type):
        if facet_type in FACET_TYPES:
            mask = FACET_TYPES[facet_type]
            return (self._data['facet_types'] & mask == mask)
        return False

    @property
    def facet_types(self):
        return [name for (name, fid) in FACET_TYPES.items()
                if self._data['facet_types'] & fid == fid]

    @classmethod
    def fetch(cls, db, paths):
        query = db.Select(sets=cls.TABLE_NAME, where=db.sqlin('path', paths))
        for row in db.fetchiter(query, paths):
            if row:
                raw_data = cls.row_to_dict(row)
                yield (raw_data['path'], raw_data)
