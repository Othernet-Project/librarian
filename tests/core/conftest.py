"""
contetst.py: fixtures for core library tests

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
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
