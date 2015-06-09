"""
exts.py: App extension container

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


class Placeholder(object):

    def __call__(self, *args, **kwargs):
        return Placeholder()

    def __getattr__(self, name):
        return Placeholder()


class ExtContainer(object):
    """Allows code which accesses pluggable extensions to still work even if
    the dependencies in question are not installed. Mainly meant to avoid
    putting boilerplate checks in such code to check for their existence.
    """
    def __init__(self):
        self._extensions = dict()

    def __get_extension(self, name):
        try:
            return self._extensions[name]
        except KeyError:
            return Placeholder

    def __setattr__(self, name, extension):
        self._extensions[name] = extension

    def __getattr__(self, name):
        return self.__get_extension(name)

    def __getitem__(self, name):
        return self.__get_extension(name)

    def is_installed(self, name):
        """Check whether extension known by `name` is installed or not."""
        return name in self._extensions
