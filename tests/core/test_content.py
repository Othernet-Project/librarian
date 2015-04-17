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
    id = '202ab62b551f6d7fc002f65652525544'
    expected = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                '255', '44']
    assert mod.content_path_components(id) == expected


def test_path_components_with_broken_id():
    """ For broken IDs, no path component should be returned """
    id = '202ab$$$62b551f6d7fc002f65652525544'
    assert mod.content_path_components(id) == []


def test_path_components_with_path():
    """ Able to split paths into components """
    path = '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace('/', os.sep)
    expected = ['202', 'ab6', '2b5', '51f', '6d7', 'fc0', '02f', '656', '525',
                '255', '44']
    assert mod.content_path_components(path) == expected


def test_path_components_with_bogus_path():
    """ For invalid paths, no components should be returned """
    path = 'foo/bar/baz'
    assert mod.content_path_components(path) == []
