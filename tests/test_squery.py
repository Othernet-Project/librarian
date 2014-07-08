"""
test_lazy.py: Unit tests for ``librarian.lazy`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
from unittest import mock

import pytest

from librarian.squery import *


@mock.patch('librarian.squery.sqlite3')
def test_connect(sqlite3):
    connect('foo')
    sqlite3.connect.assert_called_once_with('foo')


@mock.patch('librarian.squery.sqlite3')
def test_connect_stores_connection(sqlite3):
    from librarian import squery
    connect('foo')
    assert squery.DB == sqlite3.connect.return_value


@mock.patch('librarian.squery.sqlite3')
def test_disconnect(sqlite3):
    connect('foo')
    disconnect()
    sqlite3.connect.return_value.close.assert_called_once()


@mock.patch('librarian.squery.sqlite3')
def test_disconnect_removes_cached_connection(sqlite3):
    from librarian import squery
    connect('foo')
    assert squery.DB is not None
    disconnect()
    assert squery.DB == None


@mock.patch('librarian.squery.sqlite3')
def test_disconnect_with_no_connection(sqlite3):
    with pytest.raises(DBError):
        disconnect()


@mock.patch('librarian.squery.sqlite3')
def test_execute_with_new_cursor(sqlite3):
    connect('foo')
    connection = sqlite3.connect.return_value
    cursor = connection.cursor.return_value
    query('SELECT ? FROM foo;', 'bar')
    connection.cursor.assert_called_once()
    cursor.execute.assert_called_once_with('SELECT ? FROM foo;', ('bar',))


@mock.patch('librarian.squery.sqlite3')
def test_execute_with_existing_cursor(sqlite3):
    cursor = mock.Mock()
    connect('foo')
    connection = sqlite3.connection.return_value
    query('SELECT ? FROM foo;', 'bar', cursor=cursor)
    connection.cursor.assert_not_called()
    cursor.execute.assert_called_once_with('SELECT ? FROM foo;', ('bar',))


def test_query_with_kw_params():
    cursor = mock.Mock()
    query('SELECT :foo FROM :bar', foo='foo', bar='bar', cursor=cursor)
    cursor.execute.assert_called_once_with('SELECT :foo FROM :bar',
                                           {'foo': 'foo', 'bar': 'bar'})


def test_query_returns_cursor():
    cursor = mock.Mock()
    ret = query('SELECT * FROM foo', cursor=cursor)
    assert ret == cursor

