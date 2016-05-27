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
