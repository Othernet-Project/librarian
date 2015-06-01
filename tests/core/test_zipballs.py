"""
test_zipballs.py: tests related to core.zipballs module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

try:
    from unittest import mock
except:
    import mock

import pytest

from librarian.core import zipballs as mod


@mock.patch.object(mod.metadata, 'process_meta')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
@mock.patch.object(mod.json, 'load')
def test_get_metadata(load, ZipFile, process_meta):
    z = ZipFile('foo.zip')
    path = 'foo'
    ret = mod.get_metadata(z, path)
    z.open.assert_called_once_with('foo/info.json')
    zcontext = z.open.return_value.__enter__  # open is a contenxt manager
    load.assert_called_once_with(zcontext.return_value, 'utf8')
    process_meta.assert_called_once_with(load.return_value)
    assert ret == process_meta.return_value


def test_validate_no_path(*ignored):
    """ If path is empty or None, raise ValidationError """
    for path in ('', None):
        with pytest.raises(mod.ValidationError):
            mod.validate(path)


@mock.patch.object(mod.os.path, 'exists')
def test_validate_path_does_not_exists(exists):
    """ If path does not exist, raise ValidationError """
    path = '/var/spool/downloads/foo.txt'
    exists.return_value = False
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
def test_validate_wrong_extension(*ignored):
    """ If extension isn't .zip, returns False """
    path = '/var/spool/downloads/foo.txt'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
def test_validate_zipball_wrong_name(*ignored):
    """ If filename isn't MD5 hash, returns False """
    path = '/var/spool/downloads/content/foo.zip'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
def test_validate_zipball_not_zipfile(is_zipfile, *ignored):
    """ If path does not point to a valid zipfile, returns False """
    is_zipfile.return_value = False
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_has_no_md5_dir(ZipFile, is_zipfile, *ignored):
    """ If zipball doesn't contain md5 directory, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = []
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_contains_non_dir_md5(ZipFile, is_zipfile, *ignored):
    """ If zipball contains md5 path that isn't a dir, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544']
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_contains_info_json(ZipFile, is_zipfile,
                                             get_metadata):
    """ If zipball doesn't contain info.json, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_metadata.side_effect = KeyError()
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_no_valid_meta(ZipFile, is_zipfile, get_metadata):
    """
    If zipball doesn't contain metadata that can be parsed, returns False
    """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_metadata.side_effect = ValueError()
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_invalid_meta(ZipFile, is_zipfile, get_metadata):
    """ If zipball doesn't contain valid metadata keys, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_metadata.side_effect = mod.metadata.MetadataError('msg', {})
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_contains_index_html(ZipFile, is_zipfile,
                                              get_metadata, metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_metadata.return_value = metadata
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
def test_validate_zipball_contains_wrong_index_html(ZipFile, is_zipfile,
                                                    get_metadata, metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_metadata.return_value = {'index': 'foo/index.html'}
    get_metadata.return_value.update(metadata)
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
@mock.patch.object(mod.os.path, 'exists')
def test_validate_zipball_valid(exists, ZipFile, is_zipfile, get_metadata,
                                metadata):
    exists.return_value = True
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_metadata.return_value = metadata
    assert mod.validate(path) is get_metadata.return_value


@mock.patch.object(mod, 'get_metadata')
@mock.patch.object(mod.zipfile, 'is_zipfile')
@mock.patch.object(mod.zipfile, 'ZipFile', autospec=True)
@mock.patch.object(mod.os.path, 'exists')
def test_validate_zipball_valid_with_index(exists, ZipFile, is_zipfile,
                                           get_metadata, metadata):
    exists.return_value = True
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/foo/index.html']
    get_metadata.return_value = {'index': 'foo/index.html'}
    get_metadata.return_value.update(metadata)
    assert mod.validate(path) is get_metadata.return_value


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.os, 'rename')
def test_backup_returns_early_if_nothing_to_do(rename, exists):
    exists.return_value = False
    mod.backup('foo')
    assert not rename.called


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.os, 'rename')
def test_backup_normalizes(rename, exists):
    """ Backup always normalizes the path """
    exists.return_value = True
    mod.backup('\\foo\\bar\\baz')
    expected = '/foo/bar/baz'.replace('/', os.sep)
    rename.assert_called_once_with(expected, expected + '.backup')


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.os, 'rename')
def test_backup(rename, exists):
    """ Backup moves path to a path with .backup suffix """
    exists.return_value = True
    mod.backup('foo')
    rename.assert_called_once_with('foo', 'foo.backup')


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.os, 'rename')
def test_backup_returns_target_path(rename, exists):
    """ The path of the backup file/dir is returned """
    exists.return_value = True
    assert mod.backup('foo') == 'foo.backup'


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.os, 'rename')
def test_backup_returns_none_if_no_backup_is_done(rename, exists):
    """ The path of the backup file/dir is returned """
    exists.return_value = False
    assert mod.backup('foo') is None


@mock.patch.object(mod.shutil, 'rmtree')
@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.shutil, 'move')
@mock.patch.object(mod, 'backup')
@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch.object(mod.content, 'to_path')
def test_extract_success(to_path, ZipFile, backup, move, exists, rmtree):
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    target = '/srv/zipballs'
    extract_path = '/srv/zipballs/202ab62b551f6d7fc002f65652525544'
    content_path = '/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'

    to_path.return_value = content_path
    backup.return_value = '/path/to/cont.backup'
    exists.return_value = True

    assert mod.extract(path, target) == content_path

    ZipFile.assert_called_once_with(path)
    ZipFile.return_value.extractall.assert_called_once_with(target)

    backup.assert_called_once_with(content_path)
    move.assert_called_once_with(extract_path, content_path)
    exists.assert_called_once_with(backup.return_value)
    rmtree.assert_called_once_with(backup.return_value)


@mock.patch.object(mod.shutil, 'rmtree')
@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.shutil, 'move')
@mock.patch.object(mod, 'backup')
@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch.object(mod.content, 'to_path')
def test_extract_fail(to_path, ZipFile, backup, move, exists, rmtree):
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    target = '/srv/zipballs'
    extract_path = '/srv/zipballs/202ab62b551f6d7fc002f65652525544'
    content_path = '/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'

    to_path.return_value = content_path
    ZipFile.return_value.extractall.side_effect = OSError()
    exists.return_value = True

    with pytest.raises(OSError):
        mod.extract(path, target)

    ZipFile.assert_called_once_with(path)
    ZipFile.return_value.extractall.assert_called_once_with(target)
    exists.assert_called_once_with(extract_path)
    rmtree.assert_called_once_with(extract_path)
    assert not backup.called
    assert not move.called


def test_get_zip_path():
    md5 = '202ab62b551f6d7fc002f65652525544'
    basedir = '/content/path/'
    with mock.patch('os.path.exists') as exists:
        exists.return_value = True
        assert mod.get_zip_path(md5, basedir) == basedir + md5 + '.zip'

    assert mod.get_zip_path('invalid', basedir) is None


@mock.patch.object(mod.content, 'filewalk')
@mock.patch.object(mod.zipfile, 'ZipFile')
def test_create(ZipFile, filewalk):
    md5 = '202ab62b551f6d7fc002f65652525544'
    basedir = '/content/path/'

    path1 = basedir + '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44/index.html'
    path2 = basedir + '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44/s/img.jpg'
    filewalk.return_value = [path1, path2]

    mocked_zip_obj = mock.Mock()
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_zip_obj
    ZipFile.return_value = ctx_manager

    mod.create(md5, basedir)
    mocked_zip_obj.write.assert_has_calls([
        mock.call(path1, '202ab62b551f6d7fc002f65652525544/index.html'),
        mock.call(path2, '202ab62b551f6d7fc002f65652525544/s/img.jpg')
    ])


def test_get_md5_from_path():
    assert mod.get_md5_from_path('/path/to/mymd5.zip') == 'mymd5'


@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch('__builtin__.open')
def test_get_file_error_opening(file_open, ZipFile):
    file_open.side_effect = IOError()
    with pytest.raises(mod.ValidationError):
        mod.get_file('test/file.zip', 'image.jpg')

    assert not ZipFile.called


@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch('__builtin__.open')
def test_get_file_invalid_zip(file_open, ZipFile):
    ZipFile.side_effect = mod.zipfile.BadZipfile()
    with pytest.raises(mod.ValidationError):
        mod.get_file('test/file.zip', 'image.jpg')

    ZipFile.assert_called_once_with(file_open.return_value)


@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch('__builtin__.open')
def test_get_file_read(file_open, ZipFile):
    raw_file = mock.Mock()
    file_open.return_value = raw_file

    mocked_file = mock.Mock()
    mocked_file.read.return_value = 'some content'
    mocked_zipfile = mock.Mock()
    mocked_zipfile.open.return_value = mocked_file
    ZipFile.return_value = mocked_zipfile

    result = mod.get_file('test/file.zip', 'file.ext', no_read=False)
    assert result == 'some content'
    assert raw_file.close.called
    assert mocked_file.close.called
    assert mocked_file.read.called


@mock.patch.object(mod.zipfile, 'ZipFile')
@mock.patch('__builtin__.open')
def test_get_file_no_read(file_open, ZipFile):
    raw_file = mock.Mock()
    file_open.return_value = raw_file

    mocked_file = mock.Mock()
    mocked_zipfile = mock.Mock()
    mocked_zipfile.open.return_value = mocked_file
    ZipFile.return_value = mocked_zipfile

    result = mod.get_file('test/file.zip', 'file.ext', no_read=True)
    assert result is mocked_file
    assert not raw_file.close.called
    assert not mocked_file.close.called
    assert not mocked_file.read.called
