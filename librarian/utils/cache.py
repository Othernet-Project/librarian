"""
cache.py: Simple caching

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import datetime
import functools
import hashlib


_cache = dict()


def get_key(*args, **kwargs):
    """Return the md5 hash all the passed arguments."""
    md5 = hashlib.md5()

    for data in args:
        md5.update(str(data))

    for key, value in kwargs.items():
        md5.update(str(key) + str(value))

    return md5.hexdigest()


def get_expiry(expires_in):
    return datetime.datetime.now() + datetime.timedelta(seconds=expires_in)


def has_expired(expires):
    return expires < datetime.datetime.now()


def cached(expires_in=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            prefix = func.__name__
            key = get_key(prefix, *args, **kwargs)
            try:
                data = _cache[key]
                if expires_in and has_expired(data['expires']):
                    raise KeyError()
            except KeyError:
                # not found in cache, or is expired, recalculate data
                data = dict(value=func(*args, **kwargs))
                if expires_in is not None:
                    data['expires'] = get_expiry(expires_in)
                _cache[key] = data
            return data['value']
        return wrapper
    return decorator
