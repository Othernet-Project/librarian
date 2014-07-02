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
__all__ = ('Lazy', 'CachingLazy', 'lazy',)


class Lazy:
    """ Proxy object that evaluates a function when its value is needed

    The basic idea is pretty much stolen from Django's
    ``utils.functional.lazy``.
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _eval(self):
        return self._func(*self._args, **self._kwargs)

    @staticmethod
    def _eval_other(other):
        try:
            return other._eval()
        except AttributeError:
            return other

    def __repr__(self):
        return '<Lazy {}>'.format(self._func)

    def __str__(self):
        return str(self._eval())

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


class CachingLazy(Lazy):
    """ Caching version of the Lazy class """

    def __init__(self, *args, **kwargs):
        self._called = False
        self._cached = None
        super().__init__(*args, **kwargs)

    def _eval(self):
        if self._called:
            return self._cached
        self._called = True
        self._cached = self._func(*self._args, **self._kwargs)
        return self._cached


def lazy(fn, lazy_class=Lazy):
    """ Converts a function into lazily evaluated version

    The lazy object is instance of ``Lazy`` class, but this can be overridden
    by using ``lazy_class`` argument.

    :param lazy_class:  class to use for creating lazy objects
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        return lazy_class(fn, *args, **kwargs)
    return decorator


def caching_lazy(fn):
    """ Convert a function into lazily evaluated version which caches value

    This is the equivalent of using the ``lazy`` decorator with ``CachingLazy``
    class. Use this decorator as shortcut when caching behavior is needed
    (provides a more intiutive interface).
    """
    return lazy(fn, lazy_class=CachingLazy)
