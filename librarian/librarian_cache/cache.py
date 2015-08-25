"""
cache.py: Simple caching

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import time
import uuid


class BaseCache(object):
    """Abstract class, meant to be subclassed by specific caching backends to
    implement their own `get` and `set` methods.

    :param default_timeout:  timeout value to use if explicit `timeout` param
                             is omitted or `None`. `0` means no timeout.
    """
    def __init__(self, default_timeout=0, **kwargs):
        self.default_timeout = default_timeout

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
        return expires > 0 and expires < time.time()


class NoOpCache(BaseCache):
    """Dummy cache which does not perform anything"""
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
    def __init__(self, **kwargs):
        super(InMemoryCache, self).__init__(**kwargs)
        self._cache = dict()

    def get(self, key):
        try:
            (expires, data) = self._cache[key]
            if not self.has_expired(expires):
                return data
            self._cache.pop(key, None)  # delete expired data from cache
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
        for key in self._cache.keys():
            if key.startswith(prefix):
                self.delete(key)


class MemcachedCache(BaseCache):
    """Memcached based cache backend

    :param servers:  list / tuple containing memcache server address(es)
    """
    prefixes_key = '__prefix__'

    def __init__(self, servers, **kwargs):
        super(MemcachedCache, self).__init__(**kwargs)
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


def setup(backend, timeout, servers):
    """Instantiate and return the requested cache backend.

    :param backend:  string: unique backend class identifier, possible values:
                     "in-memory", "memcached"
    :param timeout:  default timeout in seconds
    :param servers:  list / tuple of server addresses
    """
    backends = {'in-memory': InMemoryCache,
                'memcached': MemcachedCache}
    try:
        backend_cls = backends[backend]
    except KeyError:
        return NoOpCache()  # caching will be disabled
    else:
        return backend_cls(default_timeout=timeout,
                           servers=servers)
