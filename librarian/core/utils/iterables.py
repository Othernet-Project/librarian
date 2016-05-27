"""
Functions and decorators for making sure the parameters they work on are of
iterable types.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import functools
import numbers


def is_integral(obj):
    """
    Determine whether the passed in object is a number of integral type.
    """
    return isinstance(obj, numbers.Integral)


def is_string(obj):
    """
    Determine if the passed in object is a string.
    """
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def is_iterable(obj):
    """
    Determine if the passed in object is an iterable, but not a string or dict.
    """
    return (hasattr(obj, '__iter__') and
            not isinstance(obj, dict) and
            not is_string(obj))


def as_iterable(params=None):
    """
    Make sure the marked parameters are iterable. In case a single-unwrapped
    parameter is found among them (e.g. an int, string, ...), wrap it in a
    list and forward like that to the wrapped function. The marked parameters,
    if not explicitly specified, defaults to the 1st argument (``args[1]``).
    """
    # set up default converter and separate positional from keyword arguments
    params = params or [1]
    indexes = [i for i in params if is_integral(i)]
    keys = [k for k in params if is_string(k)]

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # patch positional arguments, if needed
            if indexes:
                # copy `args` into a new list and wrap it's elements in a list
                # on the specified indexes, which are not iterables themselves
                args = [[x] if i in indexes and not is_iterable(x) else x
                        for (i, x) in enumerate(args)]
            # patch keyword arguments, if needed
            if keys:
                for key in keys:
                    if not is_iterable(kwargs[key]):
                        kwargs[key] = [kwargs[key]]
            # invoke ``fn`` with patched parameters
            return fn(*args, **kwargs)
        return wrapper
    return decorator
