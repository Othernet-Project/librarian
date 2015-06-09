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


@pytest.fixture(params=['pylibmc', 'memcache'])
def mc_cache(request):
    def import_mock(name, *args):
        if request.param != name:
            raise ImportError()

        client = mock.Mock()
        client.name = request.param

        client_lib = mock.Mock()
        client_lib.Client.return_value = client

        return client_lib

    with mock.patch('__builtin__.__import__', side_effect=import_mock):
        instance = mod.MemcachedCache(['127.0.0.1:11211'])
        assert instance._cache.name == request.param
        return instance


def test_generate_key(base_cache):
    known_md5 = 'f3e993b570e3ec53b3b05df933267e6f'
    generated_md5 = mod.generate_key(1, 2, 'ab', name='something')
    assert generated_md5 == known_md5


@mock.patch.object(mod, 'request')
def test_cached_no_backend(request):
    request.app.exts.cache = mod.NoOpCache()
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'data'
    cached_func = mod.cached()(orig_func)

    result = cached_func('test', a=3)
    assert result == 'data'
    orig_func.assert_called_once_with('test', a=3)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'parse_prefix')
@mock.patch.object(mod, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_found(request, generate_key, parse_prefix, get, setfunc,
                      base_cache):
    request.app.exts.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    generate_key.return_value = 'md5_key'
    parse_prefix.return_value = ''
    get.return_value = 'data'
    cached_func = mod.cached()(orig_func)

    result = cached_func('test', a=3)
    assert result == 'data'
    generate_key.assert_called_once_with('orig_func', 'test', a=3)
    get.assert_called_once_with('md5_key')
    assert not setfunc.called


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'parse_prefix')
@mock.patch.object(mod, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found(request, generate_key, parse_prefix, get, setfunc,
                          base_cache):
    request.app.exts.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    parse_prefix.return_value = ''
    generate_key.return_value = 'md5_key'
    get.return_value = None
    cached_func = mod.cached()(orig_func)

    result = cached_func('test', a=3)
    assert result == 'fresh'
    generate_key.assert_called_once_with('orig_func', 'test', a=3)
    get.assert_called_once_with('md5_key')
    setfunc.assert_called_once_with('md5_key',
                                    'fresh',
                                    timeout=base_cache.default_timeout)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'parse_prefix')
@mock.patch.object(mod, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found_no_timeout(request, generate_key, parse_prefix, get,
                                     setfunc, base_cache):
    request.app.exts.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    parse_prefix.return_value = ''
    generate_key.return_value = 'md5_key'
    get.return_value = None
    cached_func = mod.cached(timeout=0)(orig_func)

    cached_func('test', a=3)
    setfunc.assert_called_once_with('md5_key', 'fresh', timeout=0)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'parse_prefix')
@mock.patch.object(mod, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found_custom_timeout(request, generate_key, parse_prefix,
                                         get, setfunc, base_cache):
    request.app.exts.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    parse_prefix.return_value = ''
    generate_key.return_value = 'md5_key'
    get.return_value = None
    cached_func = mod.cached(timeout=180)(orig_func)

    cached_func('test', a=3)
    setfunc.assert_called_once_with('md5_key', 'fresh', timeout=180)


@mock.patch.object(mod.BaseCache, 'set')
@mock.patch.object(mod.BaseCache, 'get')
@mock.patch.object(mod.BaseCache, 'parse_prefix')
@mock.patch.object(mod, 'generate_key')
@mock.patch.object(mod, 'request')
def test_cached_not_found_custom_prefix(request, generate_key, parse_prefix,
                                        get, setfunc, base_cache):
    request.app.exts.cache = base_cache
    orig_func = mock.Mock(__name__='orig_func')
    orig_func.return_value = 'fresh'
    parse_prefix.return_value = 'test_'
    generate_key.return_value = 'md5_key'
    get.return_value = None
    cached_func = mod.cached(prefix='test_', timeout=180)(orig_func)

    cached_func('test', a=3)
    parse_prefix.assert_called_once_with('test_')
    get.assert_called_once_with('test_md5_key')
    setfunc.assert_called_once_with('test_md5_key', 'fresh', timeout=180)


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

    def test_delete(self, im_cache):
        im_cache._cache['key'] = 'test'
        im_cache.delete('key')
        assert im_cache._cache == {}
        try:
            im_cache.delete('invalid')
        except Exception as exc:
            pytest.fail('Should not raise: {0}'.format(exc))

    def test_invalidate(self, im_cache):
        im_cache._cache['pre1_key1'] = 3
        im_cache._cache['pre1_key2'] = 4
        im_cache._cache['pre2_key1'] = 5
        im_cache.invalidate('pre1')
        assert im_cache._cache == {'pre2_key1': 5}


class TestMemcachedCache(object):

    def test_no_client_lib(self):
        with pytest.raises(RuntimeError):
            with mock.patch('__builtin__.__import__', side_effect=ImportError):
                mod.MemcachedCache(['127.0.0.1:11211'])

    def test_get(self, mc_cache):
        mc_cache.get('test')
        mc_cache._cache.get.assert_called_once_with('test')

    @mock.patch.object(mod.MemcachedCache, 'get_expiry')
    def test_set(self, get_expiry, mc_cache):
        get_expiry.return_value = 'expires'
        mc_cache.set('key', 'data', timeout=120)
        mc_cache._cache.set.assert_called_once_with('key', 'data', 'expires')
        get_expiry.assert_called_once_with(120)

    def test_delete(self, mc_cache):
        mc_cache.delete('key')
        mc_cache._cache.delete.assert_called_once_with('key')

    def test_clear(self, mc_cache):
        mc_cache.clear()
        mc_cache._cache.flush_all.assert_called_once_with()

    @mock.patch.object(mod.MemcachedCache, 'set')
    @mock.patch.object(mod.uuid, 'uuid4')
    def test__new_prefix(self, uuid4, setfunc, mc_cache):
        uuid4.return_value = 'some-uuid-value'
        prefix = mc_cache._new_prefix('pre_')
        assert prefix == 'pre_some-uuid-value'
        prefix_key = mc_cache.prefixes_key + 'pre_'
        setfunc.assert_called_once_with(prefix_key, prefix, timeout=0)

    @mock.patch.object(mod.MemcachedCache, '_new_prefix')
    def test_parse_prefix(self, _new_prefix, mc_cache):
        _new_prefix.return_value = 'pre_some-uuid-value'
        prefix_key = mc_cache.prefixes_key + 'pre_'
        mc_cache._cache.get.return_value = None

        assert mc_cache.parse_prefix('pre_') == 'pre_some-uuid-value'
        mc_cache._cache.get.assert_called_once_with(prefix_key)
        _new_prefix.assert_called_once_with('pre_')

    @mock.patch.object(mod.MemcachedCache, '_new_prefix')
    def test_invalidate(self, _new_prefix, mc_cache):
        mc_cache.invalidate('test')
        _new_prefix.assert_called_once_with('test')


@mock.patch.object(mod, 'MemcachedCache')
@mock.patch.object(mod, 'InMemoryCache')
def test_setup(im_cache_cls, mc_cache_cls):
    im_cache = mock.Mock()
    im_cache_cls.return_value = im_cache
    cache = mod.setup('in-memory', 300, ['server'])
    im_cache_cls.assert_called_once_with(default_timeout=300,
                                         servers=['server'])
    assert cache is im_cache

    mc_cache = mock.Mock()
    mc_cache_cls.return_value = mc_cache
    cache = mod.setup('memcached', 400, ['server2'])
    mc_cache_cls.assert_called_once_with(default_timeout=400,
                                         servers=['server2'])
    assert cache is mc_cache

    no_cache = mod.setup('invalid', 100, ['server3'])
    assert isinstance(no_cache, mod.NoOpCache)
