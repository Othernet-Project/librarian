"""
decorators.py: registry of template helper functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


class AttrDict(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class LookupHelper(type):
    """Look up the requested helper function in the registry."""
    def __getattr__(cls, name):
        try:
            return cls.registry[name]
        except KeyError:
            raise AttributeError(name)


class template_helper(object):
    """Decorator for registring and accessing template helper functions.

    Example usage:

    >>> @template_helper()
    ... def my_func(a):
    ...     return a
    ...
    >>> my_func(3)
    3
    >>> template_helper.my_func(3)
    3
    >>> template_helper.my_func is my_func
    True
    >>> @template_helper('alias', 'nested.namespace')
    ... def my_func2(a):
    ...     return a
    ...
    >>> template_helper.nested.namespace.alias is my_func2
    True
    """
    __metaclass__ = LookupHelper
    registry = AttrDict()

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path.split('.') if path else []

    def __call__(self, fn):
        namespace = self.registry
        for segment in self.path:
            namespace.setdefault(segment, AttrDict())
            namespace = namespace[segment]

        namespace[self.name or fn.__name__] = fn
        return fn


if __name__ == "__main__":
    import doctest
    doctest.testmod()
