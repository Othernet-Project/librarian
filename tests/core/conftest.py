"""
contetst.py: fixtures for core library tests

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import shutil
import random
import hashlib
import tempfile

import pytest

from librarian.core.content import content_path_components as pathcomps


@pytest.fixture(scope='session')
def metadata():
    return {
        'url': 'test://outernet.is/',
        'title': 'Test',
        'timestamp': '2015-01-01 00:00:00 UTC',
        'broadcast': '2015-01-01',  # not currently required
        'license': 'GFDL',
    }


@pytest.yield_fixture
def md5dirs():
    """
    Generate 20 random hashes, and create MD5-base directory structures for
    them, returning the three-tuple of hashes, directories, and base directory.

    Base directory is created using ``tempfile.mkdtemp()`` call.
    """
    tmpdir = tempfile.mkdtemp()
    hashes = []
    dirs = []
    for i in range(20):
        md5 = hashlib.md5()
        md5.update(str(random.random()).encode('utf8'))
        h = md5.hexdigest()
        cpath = os.sep.join(pathcomps(h))
        dpath = os.path.join(tmpdir, cpath)
        os.makedirs(dpath)
        hashes.append(h)
        dirs.append(dpath)
    yield hashes, dirs, tmpdir
    shutil.rmtree(tmpdir)


@pytest.yield_fixture
def dirs():
    """
    Create 20 numbered directories with 20 numbered subdirs each and return a
    two-tuple consisting of a list of directories created and their base
    directory.
    """
    tmpdir = tempfile.mkdtemp()
    dirs = []
    for i in range(10):
        for n in range(10):
            dpath = os.path.join(tmpdir, str(i + 1), str(n + 1))
            os.makedirs(dpath)
            dirs.append(dpath)
    yield dirs, tmpdir
    shutil.rmtree(tmpdir)


@pytest.yield_fixture
def metadata_dir(metadata):
    """
    Two tuple consisting of md5 hash and base directory. These should match a
    directory tree constructed from the md5 hash, and the target directory
    should contain a single valid info.json file.
    """
    tmpdir = tempfile.mkdtemp()
    md5 = hashlib.md5()
    md5.update(str(random.random()))
    md5 = md5.hexdigest()
    dpath = os.path.join(tmpdir, os.sep.join(pathcomps(md5)))
    os.makedirs(dpath)
    with open(os.path.join(dpath, 'info.json'), 'wb') as f:
        json.dump(metadata, f)
    yield md5, tmpdir
    shutil.rmtree(tmpdir)


@pytest.yield_fixture
def bad_metadata_dir():
    """
    Two tuple consisting of md5 hash and base directory. These should match a
    directory tree constructed from the md5 hash, and the target directory
    should contain a single invalid info.json file.
    """
    tmpdir = tempfile.mkdtemp()
    md5 = hashlib.md5()
    md5.update(str(random.random()))
    md5 = md5.hexdigest()
    dpath = os.path.join(tmpdir, os.sep.join(pathcomps(md5)))
    os.makedirs(dpath)
    with open(os.path.join(dpath, 'info.json'), 'wb') as f:
        f.write('bogus\n')
    yield md5, tmpdir
    shutil.rmtree(tmpdir)
