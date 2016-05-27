"""
Generic data structures.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


class AttrDict(dict):
    """
    Behaves the same as a regular dictionary, with only one addition, which is
    that attributes that are not found on the dictionary object itself will be
    looked up in the data being held.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class IterLookup(object):
    """
    This object wraps an iterable, and returns an item with specified
    characteristic while also creating a lookup table of items that were
    missed speeding up lookups for those items the next time lookup is
    performed.
    """

    def __init__(self, iterable, key=lambda x: x):
        """
        The ``key`` argument can be used to specify the lookup value. This
        argument should be a function that takes an object and returns a value
        that will be used in lookups.
        """
        self.iterable = ((key(i), i) for i in iterable)
        self.lut = {}

    def get(self, val):
        if val in self.lut:
            return self.lut[val]
        for v, i in self.iterable:
            self.lut[v] = i
            if v == val:
                return i
        # The object was not found
        raise KeyError('No object for key {}'.format(val))
