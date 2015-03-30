"""
helpers.py: Helper functions for testing

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


def strip_wrappers(fn):
    """ For decorated fn, return function with stirpped decorator """
    if not hasattr(fn, 'func_closure') or not fn.func_closure:
        return fn
    for f in fn.func_closure:
        f = f.cell_contents
        if hasattr(f, '__call__'):
            return strip_wrappers(f)
    return fn
