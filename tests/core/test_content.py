"""
test_content.py: Tests related to core.content module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json

import mock
import pytest

from librarian.core import content as mod

MOD = mod.__name__

SEPARATOR = os.sep
# Mock directory tree
DIRTREE = {
    '.': ('index.html', 'static', 'articles'),
    'index.html': None,
    'static': ('favicon.ico', 'img', 'css'),
    'static/favicon.ico': None,
    'static/img': ('logo.png', 'header.jpg', 'bg.gif'),
    'static/img/logo.png': None,
    'static/img/header.jpg': None,
    'static/img/bg.gif': None,
    'static/css': ('style.css',),
    'static/css/style.css': None,
    'articles': ('article1.html', 'article2.html', 'images'),
    'articles/article1.html': None,
    'articles/article2.html': None,
    'articles/images': ('img1.svg', 'img2.jpg'),
    'articles/images/img1.svg': None,
    'articles/images/img2.jpg': None,
}


def mock_direntry(name, base_path):
    d = mock.Mock()
    d.path = '/'.join([base_path, name])
    d.name = name
    d.is_file.side_effect = lambda: '.' in name
    return d


# Simplified simulation of os.listdir()
def mock_scan(path):
    base_path = path
    if path.startswith('./'):
        path = path[2:]
    contents = DIRTREE.get(path)
    if contents is None:
        raise OSError()
    contents = [mock_direntry(n, base_path) for n in contents]
    print(path, contents)
    return contents


@pytest.yield_fixture
def mock_scandir():
    """
    Rigged version of scandir module that uses mock directory structure instead
    of a real one.
    """
    with mock.patch(MOD + '.scandir') as msc:
        msc.scandir = mock_scan
        yield msc


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
    assert mod.to_path(md5) is None
    assert mod.to_path(md5, prefix='/some/path/') is None


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


def test_fnwalk(mock_scandir):
    """
    Given base path and a matcher function, when fnwalk() is called, it returns
    an iterator that yields paths for which matcher returns True.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('.', matcher))) == [
        './articles',
        './articles/article1.html',
        './articles/article2.html',
        './articles/images',
        './articles/images/img1.svg',
        './articles/images/img2.jpg',
    ]


def test_fnwalk_shallow(mock_scandir):
    """
    Given a base path and matcher function, when fnwalk() is called with sallow
    flag, then it returns an iterator that yields only the first path matched.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('.', matcher, shallow=True))) == [
        './articles',
    ]


def test_fnwalk_match_self(mock_scandir):
    """
    Given a base path and matcher function that matches the base path, when
    fnwalk() is called, it returns an iterator that yields base path, in
    additon to other matched path.
    """
    matcher = lambda p: 'article' in p
    assert list(sorted(mod.fnwalk('articles', matcher))) == [
        'articles',
        'articles/article1.html',
        'articles/article2.html',
        'articles/images',
        'articles/images/img1.svg',
        'articles/images/img2.jpg',
    ]


@mock.patch.object(mod.scandir, 'scandir')
def test_filewalk(scandir):
    mocked_dir = mock.Mock()
    mocked_dir.is_dir.return_value = True
    mocked_dir.path = '/path/dir/'

    mocked_file = mock.Mock()
    mocked_file.is_dir.return_value = False
    mocked_file.path = '/path/dir/file.ext'

    root_dir = '/path/'

    def mocked_scandir(path):
        if path == root_dir:
            yield mocked_dir
        else:
            yield mocked_file

    scandir.side_effect = mocked_scandir
    assert list(mod.filewalk(root_dir)) == ['/path/dir/file.ext']


def test_find_content_dir(md5dirs):
    """ Should return only well-formed MD5-base paths """
    hashes, dirs, tmpdir = md5dirs
    bogus_dirs = [os.path.join(tmpdir, n) for n in ['abc',
                                                    'foo',
                                                    'bar',
                                                    'baz']]
    for d in bogus_dirs:
        os.makedirs(d)

    for d in dirs:
        os.makedirs(os.path.join(d, 'abc'))  # add subdirectories into content

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


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod, 'find_content_dirs')
def test_find_info_no_results(find_content_dirs, exists):
    find_content_dirs.return_value = ['/contentdir/cid/']
    exists.return_value = False
    assert list(mod.find_infos('/contentdir/')) == []
    find_content_dirs.assert_called_once_with('/contentdir/')


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


@mock.patch('os.stat')
@mock.patch.object(mod, 'to_path')
def test_get_content_size(to_path, stat):
    mocked_stat = mock.Mock(st_size=1024)
    stat.return_value = mocked_stat
    to_path.side_effect = lambda x, prefix: prefix + '/' + x
    assert mod.get_content_size('basedir', 'contentid') == 1024
    to_path.assert_called_once_with('contentid', prefix='basedir')
    stat.assert_called_once_with('basedir/contentid')
