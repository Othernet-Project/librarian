"""
test_zipballs.py: tests related to core.zipballs module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

try:
    from unittest import mock
except:
    import mock

from librarian.core import zipballs as mod

MOD = mod.__name__


def test_validate_wrong_extension():
    """ If extension isn't .zip, returns False """
    path = '/var/spool/downloads/foo.txt'
    assert mod.validate(path) is False


def test_validate_zipball_wrong_name():
    """ If filename isn't MD5 hash, returns False """
    path = '/var/spool/downloads/content/foo.zip'
    assert mod.validate(path) is False


@mock.patch(MOD + '.zipfile.is_zipfile')
def test_validate_zipball_not_zipfile(is_zipfile):
    """ If path does not point to a valid zipfile, returns False """
    is_zipfile.return_value = False
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    assert mod.validate(path) is False


@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_has_no_md5_dir(ZipFile, is_zipfile):
    """ If zipball doesn't contain md5 directory, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = []
    assert mod.validate(path) is False


@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_info_json(ZipFile, is_zipfile):
    """ If zipball doesn't contain info.json, returns False """
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/']
    assert mod.validate(path) is False


@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_contains_index_html(ZipFile, is_zipfile):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/info.json']
    assert mod.validate(path) is False


@mock.patch(MOD + '.zipfile.is_zipfile')
@mock.patch(MOD + '.zipfile.ZipFile', autospec=True)
def test_validate_zipball_valid(ZipFile, is_zipfile):
    is_zipfile.return_value = True
    path = '/var/spool/downloads/content/202ab62b551f6d7fc002f65652525544.zip'
    ZipFile.return_value.namelist.return_value = [
        '202ab62b551f6d7fc002f65652525544/',
        '202ab62b551f6d7fc002f65652525544/info.json',
        '202ab62b551f6d7fc002f65652525544/index.html']
    assert mod.validate(path) is True
