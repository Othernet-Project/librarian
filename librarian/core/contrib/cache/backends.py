"""
cache.py: Simple caching

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import time
import uuid

import validators as v

from .utils import strip_protocol


class BaseCache(object):
    """Abstract class, meant to be subclassed by specific caching backends to
    implement their own `get` and `set` methods.

    :param timeout: timeout value to use if explicit ``timeout`` param is
                    omitted or ``None``. ``0`` means no timeout.
    """
    class Config:
        timeout = v.istype(int)

    def __init__(self, timeout=0, **kwargs):
        self.default_timeout = timeout

    def get(self, key):
        raise NotImplementedError()

    def set(self, key, value, timeout=None):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def parse_prefix(self, prefix):
        raise NotImplementedError()

    def invalidate(self, prefix):
        """Invalidates all cached data where the cached `key` starts with the
        given prefix.

        :param prefix:  the same `prefix` string that was passed to the
                        `cached` decorator, or basically any string that was
                        used to prefix keys.
        """
        raise NotImplementedError()

    def get_expiry(self, timeout):
        if timeout is None:
            timeout = self.default_timeout

        return time.time() + timeout if timeout > 0 else timeout

    def has_expired(self, expires):
        expires = expires or 0
        return expires > 0 and expires < time.time()

    @classmethod
    def get_config_params(cls):
        """Return a dictionary containing the contents of the ``Config`` class,
        specifically pairs of parameter names and validator functions.
        """
        return dict((attr, getattr(cls.Config, attr).__func__)
                    for attr in dir(cls.Config) if not attr.startswith('_'))

    @classmethod
    def children(cls, source=None):
        """Recursively collect all subclasses of ``cls``, not just direct
        descendants.

        :param source:  On subsequent recursive calls, source will point to a
                        child class that needs to be inspected.
        """
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.children(source=child))
        return result


class NoOpCache(BaseCache):
    """Dummy cache which does not perform anything"""
    identifier = 'noop'

    def get(self, key):
        return

    def set(self, key, value, timeout=None):
        return

    def delete(self, key):
        return

    def clear(self):
        return

    def parse_prefix(self, prefix):
        return

    def invalidate(self, prefix):
        return


class InMemoryCache(BaseCache):
    """Simple in-memory cache backend"""
    identifier = 'in-memory'

    def __init__(self, **kwargs):
        super(InMemoryCache, self).__init__(**kwargs)
        self._cache = dict()

    def get(self, key):
        try:
            (expires, data) = self._cache[key]
            if not self.has_expired(expires):
                return data
            self.delete(key)  # delete expired data from cache
        except KeyError:
            return None

    def set(self, key, value, timeout=None):
        expires = self.get_expiry(timeout)
        self._cache[key] = (expires, value)

    def delete(self, key):
        self._cache.pop(key, None)

    def clear(self):
        self._cache = dict()

    def parse_prefix(self, prefix):
        return prefix

    def invalidate(self, prefix):
        for key in list(self._cache.keys()):
            if key.startswith(prefix):
                self.delete(key)


class ScoredInMemoryCache(InMemoryCache):
    """In-memory cache with a specified storage limit. Items are scored and
    each access to them increments their score. When the number of items
    exceeds the specified storage limit, the item with the lowest score is
    deleted from the cache.
    """
    identifier = 'scored-in-memory'

    class Config(InMemoryCache.Config):
        limit = v.istype(float)

    def __init__(self, limit, **kwargs):
        super(ScoredInMemoryCache, self).__init__(**kwargs)
        self.limit = int(limit)
        self._scores = dict()

    def get(self, key):
        result = super(ScoredInMemoryCache, self).get(key)
        if result:
            # set takes care of initializing the score of any item, so it is
            # assumed direct incrementation is safe
            self._scores[key] += 1
        return result

    def has_reached_limit(self):
        return self.limit and len(self._cache) == self.limit

    def perform_cleanup(self):
        # until cache size is not below the specified limit, delete the least
        # accessed items one by one
        while self._cache and self.has_reached_limit():
            lowest_scored_key = min(self._scores, key=self._scores.get)
            self.delete(lowest_scored_key)

    def set(self, key, value, timeout=None):
        if key not in self._cache:
            # perform cleanup only if we're about to add a new item. marginal
            # spikes over the limit are possible, e.g. if an item is updated,
            # but it's new size exceeds it's previous one
            self.perform_cleanup()

        super(ScoredInMemoryCache, self).set(key, value, timeout=timeout)
        # newly added item starts with score of 0, otherwise if item already
        # had a score and only it's value got updated, keep the original score
        self._scores.setdefault(key, 0)

    def delete(self, key):
        super(ScoredInMemoryCache, self).delete(key)
        self._scores.pop(key, None)

    def clear(self):
        super(ScoredInMemoryCache, self).clear()
        self._scores = dict()


class SizeScoredInMemoryCache(ScoredInMemoryCache):
    """Scored in memory cache, but limit is determined by the size of data
    being stored, not by the number of items.
    """
    identifier = 'size-scored-in-memory'

    def __init__(self, **kwargs):
        super(SizeScoredInMemoryCache, self).__init__(**kwargs)
        self._sizes = dict()
        self._cache_size = 0

    def has_reached_limit(self):
        return self.limit and self._cache_size >= self.limit

    def set(self, key, value, timeout=None):
        super(SizeScoredInMemoryCache, self).set(key, value, timeout=timeout)
        item_size = sys.getsizeof(value)
        self._sizes[key] = item_size
        self._cache_size += item_size

    def delete(self, key):
        super(SizeScoredInMemoryCache, self).delete(key)
        size = self._sizes.pop(key, 0)
        self._cache_size -= size

    def clear(self):
        super(SizeScoredInMemoryCache, self).clear()
        self._sizes = dict()
        self._cache_size = 0


class MemcachedCache(BaseCache):
    """Memcached based cache backend

    :param servers:  list of memcache server address(es)
    """
    identifier = 'memcached'
    prefixes_key = '__prefix__'

    class Config(BaseCache.Config):
        servers = v.listof(v.url)

    def __init__(self, servers, **kwargs):
        super(MemcachedCache, self).__init__(**kwargs)
        servers = map(strip_protocol, servers)
        try:
            import pylibmc
        except ImportError:
            try:
                import memcache
            except ImportError:
                raise RuntimeError("No memcache client library found.")
            else:
                self._cache = memcache.Client(servers)
        else:
            self._cache = pylibmc.Client(servers)

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value, timeout=None):
        expires = int(self.get_expiry(timeout))
        self._cache.set(key, value, expires)

    def delete(self, key):
        self._cache.delete(key)

    def clear(self):
        self._cache.flush_all()

    def _new_prefix(self, prefix):
        prefix_key = '{0}{1}'.format(self.prefixes_key, prefix)
        new_prefix = '{0}{1}'.format(prefix, uuid.uuid4())
        self.set(prefix_key, new_prefix, timeout=0)
        return new_prefix

    def parse_prefix(self, prefix):
        prefix_key = '{0}{1}'.format(self.prefixes_key, prefix)
        actual_prefix = self._cache.get(prefix_key)
        if not actual_prefix:
            actual_prefix = self._new_prefix(prefix)

        return actual_prefix

    def invalidate(self, prefix):
        self._new_prefix(prefix)
