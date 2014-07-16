"""
test_archive.py: Unit tests for ``librarian.lib.archive`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from unittest import mock

from librarian.lib import archive
from librarian.lib.archive import *

MOD = 'librarian.lib.archive.'

from utils import *


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'datetime')
@mock.patch(MOD + 'shutil')
@mock.patch(MOD + 'get_spool_zip_path')
@mock.patch(MOD + 'get_metadata')
def test_add_to_archive_moves_zipballs(gm_p, gszp_p, shutil, datetime, request):
    request.app.config = configure()
    gszp_p.side_effect = lambda s: s + '.zip'
    ret = add_to_archive(['a', 'b', 'c'])
    shutil.move.assert_has_calls([
        mock.call('a.zip', request.app.config['content.contentdir']),
        mock.call('b.zip', request.app.config['content.contentdir']),
        mock.call('c.zip', request.app.config['content.contentdir']),
    ])


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'datetime')
@mock.patch(MOD + 'shutil')
@mock.patch(MOD + 'get_spool_zip_path')
@mock.patch(MOD + 'get_metadata')
def test_add_to_archive_runs_sql_queries(gm_p, gszp_p, shutil, datetime, request):
    request.app.config = configure()
    gm_p.side_effect = lambda p: {'foo': 'bar'}
    ret = add_to_archive(['a', 'b', 'c'])
    cursor = request.db.transaction.return_value.__enter__.return_value
    cursor.executemany.assert_called_once_with(
        archive.ADD_QUERY,
        [{'md5': 'a', 'updated': datetime.now.return_value, 'foo': 'bar'},
         {'md5': 'b', 'updated': datetime.now.return_value, 'foo': 'bar'},
         {'md5': 'c', 'updated': datetime.now.return_value, 'foo': 'bar'}]
    )
    assert ret == cursor.rowcount


@mock.patch(MOD + 'os')
def test_path_space(os):
    os.statvfs.return_value.f_frsize = 2
    os.statvfs.return_value.f_bavail = 3
    os.statvfs.return_value.f_blocks = 4
    dev, free, tot = path_space('foo')
    os.stat.assert_called_with('foo')
    os.statvfs.assert_called_with('foo')
    assert dev == os.stat.return_value.st_dev
    assert free == 6
    assert tot == 8



@mock.patch(MOD + 'request')
@mock.patch(MOD + 'path_space')
def test_free_space(ps_p, request):
    request.app.config = configure(spooldir='/spool', contentdir='/content')
    ps_p.return_value = (1, 2, 3)
    ret = free_space()
    ps_p.assert_has_calls([mock.call('/spool'), mock.call('/content')])
    assert ret == ((2, 3), (2, 3), (2, 3))


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'path_space')
def test_free_space_different_drives(ps_p, request):
    request.app.config = configure(spooldir='/spool', contentdir='/content')
    return_multi(ps_p, [(1, 2, 3), (3, 4, 5)])
    ret = free_space()
    ps_p.assert_has_calls([mock.call('/spool'), mock.call('/content')])
    assert ret == ((2, 3), (4, 5), (6, 8))


@mock.patch(MOD + 'request')
def test_zipball_count_returns_aggregate(request):
    ret = zipball_count()
    request.db.query.assert_called_with(archive.COUNT_QUERY)
    assert ret == request.db.cursor.fetchone.return_value['count(*)']


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'os')
def test_archive_space_returns_zipball_space(os, request):
    request.app.config = configure(contentdir='/content')
    os.stat.return_value.st_size = 2
    os.listdir.return_value = ['a.zip', 'b.zip', 'c.zip']
    ret = archive_space_used()
    assert ret == 6


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'os')
def test_archive_space_ignores_non_zip(os, request):
    request.app.config = configure(contentdir='/content')
    os.stat.return_value.st_size = 2
    os.listdir.return_value = ['a.zip', 'b.txt', 'c.zip']
    ret = archive_space_used()
    assert ret == 4
