"""
Backend loader

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import pkgutil


class Delegator(object):

    def __init__(self):
        self.obj = None

    def __getattr__(self, name):
        assert self.obj is not None
        return getattr(self.obj, name)

    def __getitem__(self, name):
        assert self.obj is not None
        return self.obj[name]


class BackendProxy(object):

    def __init__(self):
        self.config = Delegator()
        self.storage = Delegator()
        self._loaded = False

    def __getattr__(self, name):
        if self._loaded:
            # proxy setup already completed, this attr really doesn't exist
            raise AttributeError(name)
        # proxy setup not yet complete, but module already accessed due to
        # early imports
        delegator = Delegator()
        setattr(self, name, delegator)
        return delegator

    def _get_backend_package(self, backend_path):
        backend_name = backend_path.split('.')[-1]
        try:
            # try loading from pythonpath
            return __import__(backend_path, fromlist=[backend_name])
        except ImportError:
            # backend not on pythonpath, try loading it from local package
            from . import backends
            backend_path = '.'.join([backends.__name__, backend_name])
            return __import__(backend_path, fromlist=[backend_name])

    def _install_modules(self, backend_pkg):
        # discover all the modules in the backend package and assign them to
        # this object, but wrapped in delegators too (as some of them might
        # have already been imported earlier imports than this setup code ran)
        modules = pkgutil.iter_modules(backend_pkg.__path__)
        for (module_finder, name, ispkg) in modules:
            mod = __import__('.'.join([backend_pkg.__name__, name]),
                             fromlist=[name])
            delegator = getattr(self, name)
            delegator.obj = mod

    def setup(self, backend_path, config, storage):
        # resolve config and storage objects
        self.config.obj = config
        self.storage.obj = storage
        # import chosen backend package
        backend_pkg = self._get_backend_package(backend_path)
        # allow access to this object(mostly for config and storage) from the
        # backend package
        setattr(backend_pkg, 'backend', self)
        self._install_modules(backend_pkg)
        self._loaded = True


backend = BackendProxy()
