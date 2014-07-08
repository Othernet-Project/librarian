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
def test_db_initialize(sqlite3):
    db = Database('foo')
    assert db.dbpath == 'foo'
    assert db.db is None
    assert db._cursor is None


@mock.patch('librarian.squery.sqlite3')
def test_db_repr(sqlite3):
    db = Database('foo')
    assert repr(db) == "<Database dbpath='foo'>"


@mock.patch('librarian.squery.sqlite3')
def test_db_connect(sqlite3):
    db = Database('foo')
    db.connect()
    sqlite3.connect.assert_called_once_with('foo')
    assert db.db == sqlite3.connect.return_value


@mock.patch('librarian.squery.sqlite3')
def test_db_disconnect(sqlite3):
    db = Database('foo')
    db.connect()
    db.disconnect()
    assert sqlite3.connect.return_value.close.call_count == 1
    assert db.db is None


@mock.patch('librarian.squery.sqlite3')
def test_disconnect_wihtout_connection(sqlite3):
    db = Database('foo')
    db.connect()
    db.disconnect()
    db.disconnect()
    assert sqlite3.connect.return_value.close.call_count == 1


@mock.patch('librarian.squery.sqlite3')
def test_cursor_property(sqlite3):
    db = Database('foo')
    db.connect()
    cur = db.cursor
    assert cur == sqlite3.connect.return_value.cursor.return_value


@mock.patch('librarian.squery.sqlite3')
def test_cursor_connects(sqlite3):
    db = Database('foo')
    cur = db.cursor
    assert sqlite3.connect.call_count == 1


@mock.patch('librarian.squery.sqlite3')
def test_cursor_is_cached(sqlite3):
    db = Database('foo')
    cur = db.cursor
    assert db._cursor is not None
    assert cur == db._cursor
    cur = db.cursor
    assert sqlite3.connect.call_count == 1


@mock.patch('librarian.squery.sqlite3')
def test_query_uses_cursor(sqlite3):
    # FIXME: We really should be testing if the property has been accessed
    db = Database('foo')
    db.connect()
    db.query('SELECT * FROM foo;')
    assert sqlite3.connect.return_value.cursor.call_count == 1


@mock.patch('librarian.squery.sqlite3')
def test_query_calls_execute(sqlite3):
    db = Database('foo')
    db.connect()
    db.query('SELECT * FROM foo;')
    cur = db.cursor
    cur.execute.assert_called_once_with('SELECT * FROM foo;', ())


@mock.patch('librarian.squery.sqlite3')
def test_query_with_params(sqlite3):
    db = Database('foo')
    db.connect()
    db.query('SELECT ? FROM foo;', 'bar')
    cur = db.cursor
    cur.execute.assert_called_once_with('SELECT ? FROM foo;', ('bar',))


@mock.patch('librarian.squery.sqlite3')
def test_query_with_kw_params(sqlite3):
    db = Database('foo')
    db.connect()
    db.query('SELECT :col FROM foo;', col='bar')
    db.cursor.execute.assert_called_once_with('SELECT :col FROM foo;',
                                              {'col': 'bar'})


@mock.patch('librarian.squery.sqlite3')
def test_query_returns_cursor(sqlite3):
    db = Database('foo')
    db.connect()
    ret = db.query('SELECT * FROM foo')
    assert ret == db.cursor


@mock.patch('librarian.squery.sqlite3')
def test_transaction_uses_cursor(sqlite3):
    db = Database('foo')
    with db.transaction() as cur:
        pass
    assert sqlite3.connect.return_value.cursor.called


@mock.patch('librarian.squery.sqlite3')
def test_transaction_begins_and_commits(sqlite3):
    db = Database('foo')
    with db.transaction() as cur:
        pass
    db.cursor.execute.assert_called_with('BEGIN')
    assert db.db.commit.called


@mock.patch('librarian.squery.sqlite3')
def test_transaction_rollback(sqlite3):
    db = Database('foo')
    with pytest.raises(Exception):
        with db.transaction() as cur:
            raise Exception()
    assert db.db.commit.called == False
    assert db.db.rollback.called


@mock.patch('librarian.squery.sqlite3')
def test_transaction_silent(sqlite3):
    db = Database('foo')
    with db.transaction(silent=True) as cur:
        raise Exception()
    assert True  # All ok if no exception leaks

