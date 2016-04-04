"""
facets.py: Handling metadata

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from .base import CDFObject


FACET_TYPES = {
    'generic': 1,
    'html': 2,
    'video': 4,
    'audio': 8,
    'image': 16,
}


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
