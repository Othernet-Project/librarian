"""
cache.py: Simple caching

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import functools
import hashlib
import time

from bottle import request


def cached(timeout=None):
    """Decorator that caches return values of functions that it wraps. The
    key is generated from the function's name and the parameters passed to
    it. E.g.:

    @cached(timeout=300)  # expires in 5 minutes
    def my_func(a, b, c=4):
        return (a + b) / c

    Cache key in this case is an md5 hash, generated from the combined
    values of: function's name("my_func"), and values of `a`, `b` and in
    case of keyword arguments both argument name "c" and the value of `c`.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                backend = request.app.cache
            except AttributeError:
                # no caching backend installed
                return func(*args, **kwargs)

            prefix = func.__name__
            key = backend.generate_key(prefix, *args, **kwargs)
            value = backend.get(key)
            if value is None:
                # not found in cache, or is expired, recalculate value
                value = func(*args, **kwargs)
                expires_in = timeout
                if expires_in is None:
                    expires_in = backend.default_timeout
                backend.set(key, value, timeout=expires_in)
            return value
        return wrapper
    return decorator


class BaseCache(object):
    """Abstract class, meant to be subclassed by specific caching backends to
    implement their own `get` and `set` methods.

    :param default_timeout:  timeout value to use if explicit `timeout` param
                             is omitted or `None`. `0` means no timeout.
    """
    def __init__(self, default_timeout=0):
        self.default_timeout = default_timeout

    def get(self, key):
        raise NotImplementedError()

    def set(self, key, value, timeout=None):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def get_expiry(self, timeout):
        if timeout is None:
            timeout = self.default_timeout

        return time.time() + timeout if timeout > 0 else timeout

    def has_expired(self, expires):
        return expires > 0 and expires < time.time()

    def generate_key(self, *args, **kwargs):
        """Return the md5 hash all the passed arguments."""
        md5 = hashlib.md5()

        for data in args:
            md5.update(str(data))

        for key, value in kwargs.items():
            md5.update(str(key) + str(value))

        return md5.hexdigest()


class InMemoryCache(BaseCache):
    """Simple in-memory cache backend"""
    def __init__(self, default_timeout=0):
        super(InMemoryCache, self).__init__(default_timeout=default_timeout)
        self._cache = dict()

    def get(self, key):
        try:
            (expires, data) = self._cache[key]
            if not self.has_expired(expires):
                return data
        except KeyError:
            return None

    def set(self, key, value, timeout=None):
        expires = self.get_expiry(timeout)
        self._cache[key] = (expires, value)

    def clear(self):
        self._cache = dict()
