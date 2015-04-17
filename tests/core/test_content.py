"""
test_content.py: Tests related to core.content module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from librarian.core import content as mod

MOD = mod.__name__

SEPARATOR = os.sep


def test_path_components():
    """ Path components shold be in groups of 3 characters except last one """
    md5 = '202ab62b551f6d7fc002f65652525544'
    expected = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                '255', '44']
    assert mod.content_path_components(md5) == expected


def test_path_components_with_broken_id():
    """ For broken IDs, no path component should be returned """
    md5 = '202ab$$$62b551f6d7fc002f65652525544'
    assert mod.content_path_components(md5) == []


def test_path_components_with_path():
    """ Able to split paths into components """
    path = '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace('/', os.sep)
    expected = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                '255', '44']
    assert mod.content_path_components(path) == expected


def test_path_components_with_trailing_slash():
    """ Trailing or leading slashes don't affect the result """
    path = '/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44/'.replace('/', os.sep)
    expected = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                '255', '44']
    assert mod.content_path_components(path) == expected


def test_path_components_with_bogus_path():
    """ For invalid paths, no components should be returned """
    path = 'foo/bar/baz'
    assert mod.content_path_components(path) == []


def test_conversion_to_path():
    """ For given ID, a valid path should be produced """
    md5 = '202ab62b551f6d7fc002f65652525544'
    path = '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace('/', os.sep)
    assert mod.to_path(md5) == path


def test_convert_to_path_with_bad_id():
    """ For broken ID, empty string is returned """
    md5 = '202ab$$$62b551f6d7fc002f65652525544'
    assert mod.to_path(md5) == ''


def test_convert_to_id():
    """ For given path, convert to proper MD5 hash """
    path = '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace('/', os.sep)
    md5 = '202ab62b551f6d7fc002f65652525544'
    assert mod.to_md5(path) == md5


def test_convert_bad_path_to_id():
    """ For a wrong path, id should be empty string """
    path = 'foo/bar/baz'
    assert mod.to_md5(path) == ''
