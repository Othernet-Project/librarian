"""
sqery.py: Helpers for working with databases

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import re
import sqlite3
import logging
from functools import wraps
from contextlib import contextmanager

import dateutil.parser

from bottle import request
from bottle_utils.common import basestring
from bottle_utils.lazy import CachingLazy
from sqlize import (From, Where, Group, Order, Limit, Select, Update, Delete,
                    Insert, Replace, sqlin, sqlarray)


SLASH = re.compile(r'\\')


sqlite3.register_converter('timestamp', dateutil.parser.parse)


class Row(sqlite3.Row):
    """ sqlite.Row subclass that allows attribute access to items """
    def __getattr__(self, key):
        return self[key]

    def get(self, key, default=None):
        key = str(key)
        try:
            return self[key]
        except IndexError:
            return default

    def __contains__(self, key):
        return key in self.keys()


class Connection(object):
    """ Wrapper for sqlite3.Connection object """
    def __init__(self, path=':memory:',):
        self.path = path
        self.connect()

    def connect(self):
        self._conn = sqlite3.connect(self.path,
                                     detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = Row

        # Allow manual transaction handling, see http://bit.ly/1C7E7EQ
        self._conn.isolation_level = None
        # More on WAL: https://www.sqlite.org/isolation.html
        # Requires SQLite >= 3.7.0
        cur = self._conn.cursor()
        cur.execute('PRAGMA journal_mode=WAL;')
        logging.debug('Connected to database {}'.format(self.path))

    def close(self):
        self._conn.commit()
        self._conn.close()

    def __getattr__(self, attr):
        return getattr(self._conn, attr)

    def __setattr__(self, attr, value):
        if not hasattr(self, attr) or attr == '_conn':
            object.__setattr__(self, attr, value)
        else:
            setattr(self._conn, attr, value)

    def __repr__(self):
        return "<Connection path='%s'>" % self.path


class Database(object):

    # Provide access to query classes for easier access
    sqlin = sqlin
    sqlarray = sqlarray
    From = From
    Where = Where
    Group = Group
    Order = Order
    Limit = Limit
    Select = Select
    Update = Update
    Delete = Delete
    Insert = Insert
    Replace = Replace

    def __init__(self, conn, debug=False):
        self.conn = conn
        self.debug = debug
        self._cursor = None

    def _convert_query(self, qry):
        """ Ensure any SQLExpression instances are serialized

        :param qry:     raw SQL string or SQLExpression instance
        :returns:       raw SQL string
        """
        if hasattr(qry, 'serialize'):
            qry = qry.serialize()
        assert isinstance(qry, basestring), 'Expected qry to be string'
        if self.debug:
            print('SQL:', qry)
        return qry

    def query(self, qry, *params, **kwparams):
        """ Perform a query

        Any positional arguments are converted to a list of arguments for the
        query, and are used to populate any '?' placeholders. The keyword
        arguments are converted to a mapping which provides values to ':name'
        placeholders. These do not apply to SQLExpression instances.

        :param qry:     raw SQL or SQLExpression instance
        :returns:       cursor object
        """
        qry = self._convert_query(qry)
        self.cursor.execute(qry, params or kwparams)
        return self.cursor

    def execute(self, qry, *args, **kwargs):
        qry = self._convert_query(qry)
        self.cursor.execute(qry, *args, **kwargs)

    def executemany(self, qry, *args, **kwargs):
        qry = self._convert_query(qry)
        self.cursor.executemany(qry, *args, **kwargs)

    def executescript(self, sql):
        self.cursor.executescript(sql)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
        self.conn.commit()

    def refresh_table_stats(self):
        self.execute('ANALYZE sqlite_master;')

    def acquire_lock(self):
        self.execute('BEGIN EXCLUSIVE;')

    def close(self):
        self.conn.close()
        # the cached cursor object must be reset, otherwise after reconnecting
        # it would still try to use it, and would run into the closed db issue
        self._cursor = None

    def reconnect(self):
        self.conn.connect()

    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor

    @property
    def results(self):
        return self.cursor.fetchall()

    @property
    def result(self):
        return self.cursor.fetchone()

    @contextmanager
    def transaction(self, silent=False):
        self.execute('BEGIN;')
        try:
            yield self.cursor
            self.commit()
        except Exception:
            self.rollback()
            if silent:
                return
            raise

    @classmethod
    def connect(cls, dbpath):
        return Connection(dbpath)

    def __repr__(self):
        return "<Database connection='%s'>" % self.conn.path


class DatabaseContainer(dict):
    def __init__(self, connections, debug=False):
        super(DatabaseContainer, self).__init__(
            {n: CachingLazy(Database, c, debug=debug)
             for n, c in connections.items()})
        self.__dict__ = self


def get_connection(db_name, db_path):
    # FIXME: Add unit tests
    if isinstance(db_path, Database):
        conn = db_path.conn
    else:
        if hasattr(db_path, 'cursor'):
            conn = db_path
        else:
            conn = Database.connect(db_path)
    return conn


def get_connections(db_confs):
    return {n: get_connection(n, p) for n, p in db_confs.items()}


def get_databases(db_confs, debug=False):
    conns = get_connections(db_confs)
    return DatabaseContainer(conns, debug=debug)


def database_plugin(databases):
    def plugin(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            request.db = databases
            return callback(*args, **kwargs)
        return wrapper
    return plugin
