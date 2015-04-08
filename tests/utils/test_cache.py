import datetime

import mock

from librarian.utils import cache as mod


MOD = mod.__name__


def test_get_expiry():
    result = mod.get_expiry(60)
    assert result > datetime.datetime.now()


def test_has_expired():
    minute_ago = datetime.datetime.now() - datetime.timedelta(seconds=60)
    assert mod.has_expired(minute_ago)

    in_a_minute = datetime.datetime.now() + datetime.timedelta(seconds=60)
    assert not mod.has_expired(in_a_minute)


def test_get_key():
    known_md5 = 'f3e993b570e3ec53b3b05df933267e6f'
    assert mod.get_key(1, 2, 'ab', name='something') == known_md5


@mock.patch(MOD + '._cache')
def test_cache_found_no_expiry(cache):
    test_func = mock.Mock(__name__='test_func')
    cached_func = mod.cached()(test_func)
    cache.__getitem__.return_value = {'value': 42}

    result = cached_func(1)

    assert result == 42
    assert not test_func.called
    assert not cache.__setitem__.called


@mock.patch(MOD + '.has_expired')
@mock.patch(MOD + '._cache')
def test_cache_found_not_expired(cache, has_expired):
    test_func = mock.Mock(__name__='test_func')
    cached_func = mod.cached()(test_func)
    cache.__getitem__.return_value = {'value': 42}
    has_expired.return_value = False

    result = cached_func(1)

    assert result == 42
    assert not test_func.called
    assert not cache.__setitem__.called


@mock.patch(MOD + '.has_expired')
@mock.patch(MOD + '.get_expiry')
@mock.patch(MOD + '.get_key')
@mock.patch(MOD + '._cache')
def test_cache_found_but_expired(cache, get_key, get_expiry, has_expired):
    test_func = mock.Mock(__name__='test_func', return_value=48)
    cached_func = mod.cached(expires_in=10)(test_func)
    get_key.return_value = 'unique_key'
    get_expiry.return_value = 'now'
    has_expired.return_value = True

    cache.__getitem__.return_value = {'value': 42, 'expires': 'minute ago'}

    result = cached_func(1)

    assert result == 48
    test_func.assert_called_once_with(1)
    cache.__setitem__.assert_called_once_with('unique_key', {'value': 48,
                                                             'expires': 'now'})


@mock.patch(MOD + '.get_key')
@mock.patch(MOD + '._cache')
def test_cache_not_found_no_expiry(cache, get_key):
    test_func = mock.Mock(__name__='test_func', return_value=42)
    cached_func = mod.cached()(test_func)
    cache.__getitem__.side_effect = KeyError()
    get_key.return_value = 'unique_key'

    result = cached_func(1)

    assert result == 42
    test_func.assert_called_once_with(1)
    cache.__setitem__.assert_called_once_with('unique_key', {'value': 42})


@mock.patch(MOD + '.get_expiry')
@mock.patch(MOD + '.get_key')
@mock.patch(MOD + '._cache')
def test_cache_not_found_has_expiry(cache, get_key, get_expiry):
    test_func = mock.Mock(__name__='test_func', return_value=42)
    cached_func = mod.cached(expires_in=10)(test_func)
    cache.__getitem__.side_effect = KeyError()
    get_key.return_value = 'unique_key'
    get_expiry.return_value = 'now'

    result = cached_func(1)

    assert result == 42
    test_func.assert_called_once_with(1)
    cache.__setitem__.assert_called_once_with('unique_key', {'value': 42,
                                                             'expires': 'now'})
