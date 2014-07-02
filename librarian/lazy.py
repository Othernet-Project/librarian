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

    The function will return a ``Lazy`` or ``CachingLazy`` instance, which
    evaluates the original function only when its special methods are called.

    The ``always_evaluate`` argument determines whether ``Lazy`` or
    ``CachingLazy`` instance is retruned. If ``True`` is passed, a ``Lazy``
    object is returned, which will always reevaluate the function call whenever
    the return value is actually used. Otherwise, the return value is behave
    'normally', meaning it will only cause the function call to be evaluated
    once.

    :param always_evaluate:     whether to always reevaluate the result
                                (default: ``False``)
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        return lazy_class(fn, args, kwargs)
    return decorator
