"""
lazy.py: Lazy evaluation tools

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from functools import wraps

from . import __version__ as _version, __author__ as _author

__version__ = _version
__author__ = _author
__all__ = ('Lazy', 'lazy',)


class Lazy:
    """ Proxy object that evaluates a function when its value is needed

    The proxy object will remember the function and its arguments, and return
    the value of its evaluation when some of the magic methods are accessed.
    The value is only evaluated the first time it is needed and then cached,
    so function is always evaluated once.

    The basic idea is borrowed from Django's ``utils.functional.lazy``.
    """

    def __init__(self, func, *args, **kwargs):
        self._called = False
        self._cached = None
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _eval(self):
        if self._called:
            return self._cached
        self._called = True
        self._cached = self._func(*self._args, **self._kwargs)
        return self._cached

    @staticmethod
    def _eval_other(other):
        try:
            return other._eval()
        except AttributeError:
            return other

    def __repr__(self):
        return '<Lazy {}>'.format(self._func)

    def __str__(self):
        return self._eval()

    def __bytes__(self):
        return bytes(self._eval())

    def __call__(self):
        return self._eval()()

    def __format__(self, format_spec):
        return self._eval().__format__(format_spec)

    # Being explicit about all comparison methods to avoid double-calls

    def __lt__(self, other):
        other = self._eval_other(other)
        return self._eval() < other

    def __le__(self, other):
        other = self._eval_other(other)
        return self._eval() <= other

    def __gt__(self, other):
        other = self._eval_other(other)
        return self._eval() > other

    def __ge__(self, other):
        other = self._eval_other(other)
        return self._eval() >= other

    def __eq__(self, other):
        other = self._eval_other(other)
        return self._eval() == other

    def __ne__(self, other):
        other = self._eval_other(other)
        return self._eval() != other

    # We mostly use this for strings, so having just __add__ is fine

    def __add__(self, other):
        other = self._eval_other(other)
        return self._eval() + other

    def __bool__(self):
        return bool(self._eval())

    def __hash__(self):
        return hash(self._eval())


def lazy(fn):
    """ Decorator that converts a function into lazily evaluated version

    The function will return a ``Lazy`` or ``CachingLazy`` instance, which
    evaluates the original function only when its special methods are called.
    """

    @wraps(fn)
    def decorator(*args, **kwargs):
        return Lazy(fn, args, kwargs)
    return decorator
