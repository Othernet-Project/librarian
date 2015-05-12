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

MOD = mod.__name__


@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.json.load')
def test_get_info(load, ZipFile):
    z = ZipFile('foo.zip')
    path = 'foo'
    ret = mod.get_info(z, path)
    z.open.assert_called_once_with('foo/info.json')
    zcontext = z.open.return_value.__enter__  # open is a contenxt manager
    load.assert_called_once_with(zcontext.return_value, 'utf8')
    assert ret == load.return_value


@mock.patch(MOD + '.get_info')
def test_validate_wrong_extension(*ignored):
    """ If extension isn't .zip, returns False """
    path = '/var/spool/downloads/foo.txt'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
def test_validate_zipball_wrong_name(*ignored):
    """ If filename isn't MD5 hash, returns False """
    path = '/var/spool/downloads/content/foo.zip'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
def test_validate_zipball_not_zipfile(is_zipfile, *ignored):
    """ If path does not point to a valid zipfile, returns False """
    is_zipfile.return_value = False
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_has_no_md5_dir(ZipFile, is_zipfile, *ignored):
    """ If zipball doesn't contain md5 directory, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = []
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_non_dir_md5(ZipFile, is_zipfile, *ignored):
    """ If zipball contains md5 path that isn't a dir, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544']
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_info_json(ZipFile, is_zipfile, get_info):
    """ If zipball doesn't contain info.json, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_info.side_effect = KeyError
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_no_valid_meta(ZipFile, is_zipfile, get_info):
    """
    If zipball doesn't contain metadata that can be parsed, returns False
    """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_info.side_effect = ValueError
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_no_valid_meta_keys(ZipFile, is_zipfile, get_info):
    """ If zipball doesn't contain valid metadata keys, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_info.return_value = {}
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_index_html(ZipFile, is_zipfile, get_info,
                                              metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    get_info.return_value = metadata
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_wrong_index_html(ZipFile, is_zipfile,
                                                    get_info, metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_info.return_value = {'index': 'foo/index.html'}
    get_info.return_value.update(metadata)
    with pytest.raises(mod.ValidationError):
        mod.validate(path)


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_valid(ZipFile, is_zipfile, get_info, metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/index.html']
    get_info.return_value = metadata
    assert mod.validate(path) is get_info.return_value


@mock.patch(MOD + '.get_info')
@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_valid_with_index(ZipFile, is_zipfile, get_info,
                                           metadata):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/foo/index.html']
    get_info.return_value = {'index': 'foo/index.html'}
    get_info.return_value.update(metadata)
    assert mod.validate(path) is get_info.return_value


@mock.patch(MOD + '.os.path.exists')
@mock.patch(MOD + '.os.rename')
def test_backup_returns_early_if_nothing_to_do(rename, exists):
    exists.return_value = False
    mod.backup('foo')
    assert not rename.called


@mock.patch(MOD + '.os.rename')
@mock.patch(MOD + '.os.path.exists')
def test_backup_normalizes(exists, rename):
    """ Backup always normalizes the path """
    exists.return_value = True
    mod.backup('\\foo\\bar\\baz')
    expected = '/foo/bar/baz'.replace('/', os.sep)
    rename.assert_called_once_with(expected, expected + '.backup')


@mock.patch(MOD + '.os.path.exists')
@mock.patch(MOD + '.os.rename')
def test_backup(rename, exists):
    """ Backup moves path to a path with .backup suffix """
    exists.return_value = True
    mod.backup('foo')
    rename.assert_called_once_with('foo', 'foo.backup')


@mock.patch(MOD + '.os.path.exists')
@mock.patch(MOD + '.os.rename')
def test_backup_returns_target_path(rename, exists):
    """ The path of the backup file/dir is returned """
    exists.return_value = True
    assert mod.backup('foo') == 'foo.backup'


@mock.patch(MOD + '.os.path.exists')
@mock.patch(MOD + '.os.rename')
def test_backup_returns_none_if_no_backup_is_done(rename, exists):
    """ The path of the backup file/dir is returned """
    exists.return_value = False
    assert mod.backup('foo') is None


@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.content.to_path')
def test_extract_to_tempdir(to_path, ZipFile, gettempdir, *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    mod.extract(path, '/srv/zipballs')
    ZipFile.return_value.extractall.assert_called_once_with(
        gettempdir.return_value)


@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.content.to_path')
def test_creates_target_dir(to_path, move, gettempdir, *ignored):
    md5_parts = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                 '255', '44']
    to_path.return_value = ('/srv/zipballs/' + '/'.join(md5_parts))
    gettempdir.return_value = '/tmp/dir/'
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    mod.extract(path, '/srv/zipballs')
    move.assert_called_once_with(gettempdir.return_value + ''.join(md5_parts),
                                 to_path.return_value)


@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.content.to_path')
def test_extract_backs_up(to_path, backup, gettempdir, *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    mod.extract(path, '/srv/zipballs')
    backup.assert_called_once_with(to_path.return_value)


@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.content.to_path')
def test_extract_dir_is_moved(to_path, move, gettempdir, *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    gettempdir.return_value = '/tmp'
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    mod.extract(path, '/srv/zipballs')
    move.assert_called_once_with('/tmp/202ab62b551f6d7fc002f65652525544',
                                 to_path.return_value)


@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.content.to_path')
def test_extract_backup_removed(to_path, rmtree, backup, gettempdir,
                                *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    gettempdir.return_value = '/tmp'
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    backup.return_value = 'foo.backup'
    mod.extract(path, '/srv/zipballs')
    rmtree.assert_called_once_with('foo.backup')


@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.content.to_path')
def test_extract_no_backup(to_path, rmtree, backup, gettempdir,
                           *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    gettempdir.return_value = '/tmp'
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    backup.return_value = None
    mod.extract(path, '/srv/zipballs')
    assert not rmtree.called


@mock.patch(MOD + '.backup')
@mock.patch(MOD + '.shutil.move')
@mock.patch(MOD + '.shutil.rmtree')
@mock.patch(MOD + '.os.makedirs')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
@mock.patch(MOD + '.tempfile.gettempdir')
@mock.patch(MOD + '.content.to_path')
def test_extract_target_path_returned(to_path, gettempdir, *ignored):
    to_path.return_value = ('/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525'
                            '/255/44')
    gettempdir.return_value = '/tmp'
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    assert mod.extract(path, '/srv/zipballs') == to_path.return_value
