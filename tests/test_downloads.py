"""
test_downloads.py: Unit tests for ``librarian.downloads`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import itertools
from unittest import mock

import pytest

from librarian.downloads import *
from librarian.content_crypto import DecryptionError


# This seems to be the best way to obtain the UnicodeDecodeError object.
# See: http://stackoverflow.com/a/6849485/234932
RAISE_UNICODE_EXCEPTION = lambda s: 'a'.encode('utf16').decode('utf8')
MOD = 'librarian.downloads'


def configure(**kwargs):
    """ Helper that provides a mock config dict """
    opts = {
        'content.spooldir': '/foo',
        'content.extension': 'sig',
        'content.keep': '12',
        'content.keyring': '/bar',
        'content.output_ext': 'zip',
        'content.metadata': 'info.json',
        'content.contentdir': '/foo',
    }
    kwargs = {'content.' + k: v for k, v in kwargs.items()}
    opts.update(kwargs)
    return opts


def return_multi(mock_object, iterable):
    """ Makes the mock object to return from the iterator """
    rvals = itertools.cycle(iterable)
    def iter_return(*args, **kwargs):
        return next(rvals)
    mock_object.side_effect = iter_return


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.os.listdir')
def test_find_signed_uses_config(listdir, request):
    request.app.config = configure()
    find_signed()
    listdir.assert_called_once_with('/foo')


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.os.listdir')
def test_find_signed_filters_by_extension(listdir, request):
    request.app.config = configure()
    listdir.return_value = ['1', '2.sig', '3.sig', '4.txt', '5.zip']
    ret = list(find_signed())
    assert ret == ['/foo/2.sig', '/foo/3.sig']
    request.app.config = configure(extension='txt')
    ret = list(find_signed())
    assert ret == ['/foo/4.txt']


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.datetime')
@mock.patch('librarian.downloads.timedelta')
def test_is_expired_uses_keep(timedelta, datetime, request):
    request.app.config = configure()
    timedelta.side_effect = lambda days: days
    datetime.fromtimestamp.side_effect = lambda secs: secs
    datetime.now.return_value = 16
    is_expired(12)
    timedelta.assert_called_with(days=12)
    request.app.config = configure(keep='6')
    is_expired(12)
    timedelta.assert_called_with(days=6)


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.datetime')
@mock.patch('librarian.downloads.timedelta')
def test_is_expired_tests_expiration(timedelta, datetime, request):
    request.app.config = configure()
    timedelta.side_effect = lambda days: days
    datetime.fromtimestamp.side_effect = lambda secs: secs
    datetime.now.return_value = 16
    assert is_expired(12) == False
    assert is_expired(2) == True
7

@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.path.getmtime')
@mock.patch('librarian.downloads.os.unlink')
def test_cleanup_unlinks_old(unlink, getmtime, is_expired_p):
    return_multi(is_expired_p, [True, False, True])
    cleanup(['foo', 'bar', 'baz'])
    assert unlink.call_count == 2
    unlink.assert_has_calls([mock.call('foo'), mock.call('baz')])


@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.path.getmtime')
@mock.patch('librarian.downloads.os.unlink')
def test_cleanup_returns_kept(unlink, getmtime, is_expired_p):
    return_multi(is_expired_p, [True, False, True])
    ret = cleanup(['foo', 'bar', 'baz'])
    assert ret == ['bar']


@mock.patch('librarian.downloads.find_signed')
@mock.patch('librarian.downloads.cleanup')
def test_get_decryptable(cleanup, find_signed):
    ret = get_decryptable()
    assert ret == cleanup.return_value


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.extract_content')
@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.unlink')
@mock.patch('librarian.downloads.partial')
def test_decrypt_uses_config(partial, unlink, is_expired_p, extract_content,
                             request):
    request.app.config = configure()
    decrypt_all(['foo', 'bar', 'baz'])
    partial.assert_called_once_with(extract_content, keyring='/bar',
                                    output_dir='/foo', output_ext='zip')


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.extract_content')
@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.unlink')
@mock.patch('librarian.downloads.partial')
def test_decrypt_extracts(partial, unlink, is_extract_p, extract_content,
                          request):
    request.app.config = configure()
    decrypt_all(['foo', 'bar', 'baz'])
    extract = partial.return_value
    assert extract.call_count == 3
    extract.assert_calls(mock.call('foo'), mock.call('bar'), mock.call('baz'))


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.extract_content')
@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.unlink')
@mock.patch('librarian.downloads.partial')
def test_decrypt_removes_extracted(partial, unlink, is_extract_p,
                                   extract_content, request):
    request.app.config = configure()
    decrypt_all(['foo', 'bar', 'baz'])
    assert unlink.call_count == 3
    unlink.assrt_calls(mock.call('foo'), mock.call('bar'), mock.call('baz'))


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.extract_content')
@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.unlink')
@mock.patch('librarian.downloads.partial')
def test_decrypt_return_values(partial, unlink, is_extract_p, extract_content,
                               request):
    request.app.config = configure()
    extract = partial.return_value
    extract.side_effect = lambda s: s + '-extracted'
    extracted, errors = decrypt_all(['foo', 'bar', 'baz'])
    assert extracted == ['foo-extracted', 'bar-extracted', 'baz-extracted']
    assert errors == []


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.extract_content')
@mock.patch('librarian.downloads.is_expired')
@mock.patch('librarian.downloads.os.unlink')
@mock.patch('librarian.downloads.partial')
def test_decrypt_return_values(partial, unlink, is_extract_p, extract_content,
                               request):
    request.app.config = configure()
    extract = partial.return_value
    extract.side_effect = DecryptionError('could not extract foo', 'foo')
    extracted, errors = decrypt_all(['foo', 'bar', 'baz'])
    assert extracted == []
    assert len(errors) == 3
    assert isinstance(errors[0], DecryptionError)


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.os')
def test_get_zipballs_uses_spooldir(os, request):
    request.app.config = configure()
    get_zipballs()
    os.listdir.assert_called_with('/foo')


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.os')
def test_get_zipballs_returns_full_paths(os, request):
    request.app.config = configure()
    os.listdir.return_value = ['foo.zip', 'bar.zip', 'baz.zip']
    os.path.join = lambda a, b: a + '/' + b
    ret = list(get_zipballs())
    assert ret == ['/foo/foo.zip', '/foo/bar.zip', '/foo/baz.zip']


@mock.patch('librarian.downloads.os')
def test_get_timestamp(os):
    ret = get_timestamp('foo')
    os.stat.assert_called_once_with('foo')
    assert ret == os.stat.return_value.st_mtime


def test_get_md5_from_path():
    ret = get_md5_from_path('/foo/1e43d05c85612e500c5d244394e24ec3.zip')
    assert ret == '1e43d05c85612e500c5d244394e24ec3'
    # It actually works from any file name, not necessarily MD5
    ret = get_md5_from_path('/foo/bar/baz')
    assert ret == 'baz'


@mock.patch('librarian.downloads.zipfile')
@mock.patch('librarian.downloads.closing')
def test_get_file_extracts_from_zip(closing, zipfile):
    get_file('foo.zip', 'bar.txt')
    zipfile.is_zipfile.assert_called_once_with('foo.zip')
    zipfile.ZipFile.assert_called_once_with('foo.zip', 'r')
    zipball = closing.return_value.__enter__.return_value
    zipball.getinfo.assert_called_once_with('foo/bar.txt')
    zipball.open.assert_called_once_with('foo/bar.txt', 'r')


@mock.patch('librarian.downloads.zipfile')
@mock.patch('librarian.downloads.closing')
def test_get_file_return_values(closing, zipfile):
    meta, content = get_file('foo.zip', 'bar.txt')
    zipball = closing.return_value.__enter__.return_value
    assert meta == zipball.getinfo.return_value
    assert content == zipball.open.return_value


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.get_file')
@mock.patch('librarian.downloads.json')
def test_get_meta_uses_metadata_setting(json, get_file, request):
    request.app.config = configure()
    mock_file = mock.Mock()
    mock_file.read.return_value = bytes('foo', encoding='utf8')
    get_file.return_value = ('meta', mock_file,)
    get_metadata('foo.zip')
    get_file.assert_called_with('foo.zip', 'info.json')
    request.app.config = configure(metadata='foo.txt')
    get_metadata('foo.zip')
    get_file.assert_called_with('foo.zip', 'foo.txt')


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.get_file')
@mock.patch('librarian.downloads.json')
def test_get_meta_parses_json(json, get_file, request):
    request.app.config = configure()
    mock_file = mock.Mock()
    mock_file.read.return_value = bytes('foo', encoding='utf8')
    get_file.return_value = ('meta', mock_file,)
    ret = get_metadata('foo.zip')
    json.loads.assert_called_once_with('foo')
    assert ret == json.loads.return_value


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.get_file')
@mock.patch('librarian.downloads.json')
def test_get_meta_invalid_json(json, get_file, request):
    request.app.config = configure()
    mock_file = mock.Mock()
    mock_file.read.return_value = bytes('foo', encoding='utf8')
    get_file.return_value = ('meta', mock_file,)
    json.loads.side_effect = ValueError()
    with pytest.raises(ContentError):
        get_metadata('foo.zip')


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.json')
@mock.patch('builtins.str')
def test_get_meta_invalid_json(str_p, json, request):
    request.app.config = configure()
    str_p.side_effect = RAISE_UNICODE_EXCEPTION
    with pytest.raises(ContentError):
        get_metadata('foo.zip')


@mock.patch('librarian.downloads.os')
def test_get_zip_path_in(os):
    os.path.exists.return_value = True
    os.path.join.return_value = '/foo/foobar.zip'
    ret = get_zip_path_in('foobar', '/foo')
    os.path.join.assert_called_with('/foo', 'foobar.zip')
    assert ret == '/foo/foobar.zip'


@mock.patch('librarian.downloads.os')
def test_get_zip_path_in_returns_none(os):
    os.path.exists.return_value = False
    os.path.join.return_value = '/foo/foobar.zip'
    ret = get_zip_path_in('foobar', '/foo')
    assert ret is None


@mock.patch('librarian.downloads.request')
@mock.patch('librarian.downloads.get_zip_path_in')
def test_get_zip_path(get_zip_path_in_p, request):
    request.app.config = configure()
    get_zip_path('foo')
    get_zip_path_in_p.assert_called_with('foo', '/foo')
    request.app.config = configure(contentdir='/bar')
    get_zip_path('bar')
    get_zip_path_in_p.assert_called_with('bar', '/bar')


