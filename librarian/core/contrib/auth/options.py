"""
options.py: User options management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import copy
import json

from ..databases.serializers import DateTimeDecoder, DateTimeEncoder


class Options(object):
    """A dict-like object with a callback that is invoked when changes are made
    to the object's state."""
    _collectors = dict()
    _processors = dict()

    def __init__(self, data, onchange):
        self.onchange = onchange
        if isinstance(data, dict):
            self.__data = data
        else:
            self.__data = json.loads(data or '{}', cls=DateTimeDecoder)

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def items(self):
        return self.__data.items()

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value
        self.onchange()

    def __contains__(self, key):
        return key in self.__data

    def __delitem__(self, key):
        del self.__data[key]
        self.onchange()

    def __len__(self):
        return len(self.__data)

    def to_json(self):
        return json.dumps(self.__data, cls=DateTimeEncoder)

    def to_native(self):
        return copy.copy(self.__data)

    def collect(self):
        for name, collector in self._collectors.items():
            self[name] = collector(self)

    def process(self, *only_these):
        for (name, processors) in self._processors.items():
            for (fn, is_explicit) in processors:
                # if `only_these` contains option names, execute only those
                # processors which name is in the list and were marked as
                # explicit processors.
                # if `only_these is empty, execute all non-explicit processors
                if ((not only_these and not is_explicit) or
                        (is_explicit and name in only_these)):
                    value = self.get(name)
                    fn(self, value)

    @classmethod
    def add_collector(cls, name, fn):
        cls._collectors[name] = fn

    @classmethod
    def collector(cls, name):
        """Register an option collector function."""
        def decorator(fn):
            cls.add_collector(name, fn)
            return fn
        return decorator

    @classmethod
    def add_processor(cls, name, fn, is_explicit):
        cls._processors.setdefault(name, [])
        cls._processors[name].append((fn, is_explicit))

    @classmethod
    def processor(cls, name, is_explicit=False):
        """Register an option processor function.

        :param name:         name of the option to be processed by `fn`
        :param is_explicit:  processor may be invoked only by explicit call
        """
        def decorator(fn):
            cls.add_processor(name, fn, is_explicit)
            return fn
        return decorator
