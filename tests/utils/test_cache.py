import time

import mock
import pytest

from librarian.utils import cache as mod


@pytest.fixture
def base_cache():
    return mod.BaseCache()


@pytest.fixture
def im_cache():
    return mod.InMemoryCache()


@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod, 'request')
def test_cached_no_backend(request, get):
    request.app = None
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'data'
    cached_func = mod.cached()(orig_func)

    result = cached_func('test', a=3)
    assert result == 'data'
    orig_func.assert_called_once_with('test', a=3)
    assert not get.called


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_found(request, generate_key, get, setfunc, base_cache):
    request.app.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    cached_func = mod.cached()(orig_func)
    generate_key.return_value = 'md5_key'
    get.return_value = 'data'

    result = cached_func('test', a=3)
    assert result == 'data'
    generate_key.assert_called_once_with('orig_func', 'test', a=3)
    get.assert_called_once_with('md5_key')
    assert not setfunc.called


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found(request, generate_key, get, setfunc, base_cache):
    request.app.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    cached_func = mod.cached()(orig_func)
    generate_key.return_value = 'md5_key'
    get.return_value = None

    result = cached_func('test', a=3)
    assert result == 'fresh'
    generate_key.assert_called_once_with('orig_func', 'test', a=3)
    get.assert_called_once_with('md5_key')
    setfunc.assert_called_once_with('md5_key',
                                    'fresh',
                                    timeout=base_cache.default_timeout)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found_no_timeout(request, generate_key, get, setfunc,
                                     base_cache):
    request.app.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    cached_func = mod.cached(timeout=0)(orig_func)
    generate_key.return_value = 'md5_key'
    get.return_value = None

    cached_func('test', a=3)
    setfunc.assert_called_once_with('md5_key', 'fresh', timeout=0)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found_custom_timeout(request, generate_key, get, setfunc,
                                         base_cache):
    request.app.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    cached_func = mod.cached(timeout=180)(orig_func)
    generate_key.return_value = 'md5_key'
    get.return_value = None

    cached_func('test', a=3)
    setfunc.assert_called_once_with('md5_key', 'fresh', timeout=180)


class TestBaseCache(object):

    def test_get_expiry(self, base_cache):
        assert base_cache.get_expiry(60) > time.time()
        assert base_cache.get_expiry(None) == 0
        assert base_cache.get_expiry(0) == 0

    def test_has_expired(self, base_cache):
        assert not base_cache.has_expired(0)
        assert not base_cache.has_expired(None)
        assert not base_cache.has_expired(time.time() + 100)
        assert base_cache.has_expired(time.time() - 100)

    def test_get_key(self, base_cache):
        known_md5 = 'f3e993b570e3ec53b3b05df933267e6f'
        generated_md5 = base_cache.generate_key(1, 2, 'ab', name='something')
        assert generated_md5 == known_md5


class TestInMemoryCache(object):

    @mock.patch.object(mod.InMemoryCache, 'has_expired')
    def test_get_found(self, has_expired, im_cache):
        has_expired.return_value = False
        im_cache._cache['key'] = ('expires', 'data')
        assert im_cache.get('key') == 'data'
        has_expired.assert_called_once_with('expires')

    @mock.patch.object(mod.InMemoryCache, 'has_expired')
    def test_get_found_expired(self, has_expired, im_cache):
        has_expired.return_value = True
        im_cache._cache['key'] = ('expires', 'data')
        assert im_cache.get('key') is None
        has_expired.assert_called_once_with('expires')

    @mock.patch.object(mod.InMemoryCache, 'has_expired')
    def test_get_not_found(self, has_expired, im_cache):
        assert im_cache.get('key') is None
        assert not has_expired.called

    @mock.patch.object(mod.InMemoryCache, 'get_expiry')
    def test_set(self, get_expiry, im_cache):
        timeout = 300
        get_expiry.return_value = 'expires'
        im_cache.set('key', 'data', timeout=timeout)
        get_expiry.assert_called_once_with(timeout)
        assert im_cache._cache['key'] == ('expires', 'data')

    def test_clear(self, im_cache):
        im_cache._cache['key'] = 'test'
        im_cache.clear()
        assert im_cache._cache == {}
