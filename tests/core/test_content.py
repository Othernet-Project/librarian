"""
test_content.py: Tests related to core.content module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json

import pytest

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


def test_convert_to_path_with_prefix():
    """ For given id and prefix, a prefixed path is gnerated """
    md5 = '202ab62b551f6d7fc002f65652525544'
    path = '/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace(
        '/', os.sep)
    assert mod.to_path(md5, prefix='/srv/zipballs') == path


def test_prefixes_are_always_normalized():
    """
    Regardless of the type of slash used in prefix, correct ones are always
    used in the output
    """
    md5 = '202ab62b551f6d7fc002f65652525544'
    path = '/srv/zipballs/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace(
        '/', os.sep)
    assert mod.to_path(md5, prefix='\\srv\\zipballs') == path
    assert mod.to_path(md5, prefix='/srv/zipballs') == path


def test_convert_to_id():
    """ For given path, convert to proper MD5 hash """
    path = '202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'.replace('/', os.sep)
    md5 = '202ab62b551f6d7fc002f65652525544'
    assert mod.to_md5(path) == md5


def test_convert_bad_path_to_id():
    """ For a wrong path, id should be empty string """
    path = 'foo/bar/baz'
    assert mod.to_md5(path) == ''


def test_fnwalk(dirs):
    """ Can walk a directory tree using a matcher function """
    names, tmpdir = dirs
    matcher = lambda p: p.endswith('7')
    ret = list(mod.fnwalk(tmpdir, matcher))
    ret.sort()
    assert ret == [
        '{}/1/7'.format(tmpdir),
        '{}/10/7'.format(tmpdir),
        '{}/2/7'.format(tmpdir),
        '{}/3/7'.format(tmpdir),
        '{}/4/7'.format(tmpdir),
        '{}/5/7'.format(tmpdir),
        '{}/6/7'.format(tmpdir),
        '{}/7'.format(tmpdir),
        '{}/7/7'.format(tmpdir),
        '{}/8/7'.format(tmpdir),
        '{}/9/7'.format(tmpdir),
    ]


def test_fnwalk_true(dirs):
    """
    If matcher always returns True, all possible paths are returned, including
    the base directory.
    """
    names, tmpdir = dirs
    matcher = lambda p: True
    ret = list(mod.fnwalk(tmpdir, matcher))
    assert set(names).issubset(set(ret))
    assert tmpdir in ret


def test_fnwalk_false(dirs):
    """
    If matcher always returns False, none of the directories are returned
    """
    names, tmpdir = dirs
    matcher = lambda p: False
    ret = list(mod.fnwalk(tmpdir, matcher))
    assert ret == []


def test_find_content_dir(md5dirs):
    """ Should return only well-formed MD5-base paths """
    hashes, dirs, tmpdir = md5dirs
    bogus_dirs = [os.path.join(tmpdir, n) for n in ['foo', 'bar', 'baz']]
    for d in bogus_dirs:
        os.makedirs(d)
    ret = list(mod.find_content_dirs(tmpdir))
    dirs.sort()
    ret.sort()
    assert ret == dirs


def test_find_infos(md5dirs, metadata):
    hashes, dirs, tmpdir = md5dirs
    for d in dirs:
        with open(os.path.join(d, 'info.json'), 'wb') as f:
            json.dump(metadata, f)
    for infopath, data, md5 in mod.find_infos(tmpdir):
        assert md5 in hashes
        assert os.path.dirname(infopath) in dirs
        assert infopath.endswith('info.json')
        assert data == metadata


def test_get_meta(metadata_dir, metadata):
    """ Load and parse metadata from md5-based dir stcture under base dir """
    md5, tmpdir = metadata_dir
    ret = mod.get_meta(tmpdir, md5)
    assert ret == metadata


def test_get_meta_with_missing_metadta(md5dirs):
    hashes, dirs, tmpdir = md5dirs
    md5 = hashes[0]
    with pytest.raises(IOError):
        mod.get_meta(tmpdir, md5)


def test_get_meta_with_bad_metadta(bad_metadata_dir, metadata):
    md5, tmpdir = bad_metadata_dir
    with pytest.raises(ValueError):
        mod.get_meta(tmpdir, md5)
