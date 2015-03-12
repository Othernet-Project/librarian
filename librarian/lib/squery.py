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
from functools import wraps
from contextlib import contextmanager

import dateutil.parser
from bottle import request

from .gspawn import call


SLASH = re.compile(r'\\')


sqlite3.register_converter('timestamp', dateutil.parser.parse)


def normurl(url):
    """ Replace backslashes with forward slashes """
    return SLASH.sub('/', url)


class Row(sqlite3.Row):
    """ sqlite.Row subclass that allows attribute access to items """
    def __getattr__(self, key):
        return self[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except IndexError:
            return default

    def __contains__(self, key):
        return key in self.keys()


class Database(object):
    def __init__(self, conn, debug=False):
        self.conn = conn
        self.debug = debug
        self._cursor = None

    def _convert_query(self, qry):
        """ Ensure any SQLExpression instances are serialized

        :param qry:     raw SQL string or SQLExpression instance
        :returns:       raw SQL string
        """
        if hasattr(qry, '__sqlrepr__'):
            return qry.__sqlrepr__(qry)
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
        call(self.cursor.execute, qry, params or kwparams)
        return self.cursor

    def execute(self, qry, *args, **kwargs):
        qry = self._convert_query(qry)
        call(self.cursor.execute, qry, *args, **kwargs)

    def executemany(self, qry, *args, **kwargs):
        qry = self._convert_query(qry)
        call(self.cursor.executemany, qry, *args, **kwargs)

    def executescript(self, sql):
        call(self.cursor.executescript, sql)

    def commit(self):
        call(self.conn.commit)

    def rollback(self):
        call(self.conn.rollback)

    def refresh_table_stats(self):
        self.execute('ANALYZE sqlite_master;')

    def acquire_lock(self):
        self.conn.interrupt()
        self.execute('BEGIN EXCLUSIVE')

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor

    @property
    def results(self):
        return call(self.cursor.fetchall)

    @property
    def result(self):
        return call(self.cursor.fetchone)

    @contextmanager
    def transaction(self, silent=False):
        self.execute('BEGIN')
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
        db = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = Row
        # Allow manual transaction handling, see http://bit.ly/1C7E7EQ
        db.isolation_level = None
        # More on WAL: https://www.sqlite.org/isolation.html
        # Requires SQLite >= 3.7.0
        cur = db.cursor()
        cur.execute('PRAGMA journal_mode=WAL')
        return db

    def __repr__(self):
        return "<Database connection='%s'>" % self.conn


def database_plugin(dbpath, debug=False):
    if hasattr(dbpath, 'cursor'):
        conn = dbpath
    else:
        conn = Database.connect(dbpath)
    def plugin(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            request.db = Database(conn, debug=debug)
            return callback(*args, **kwargs)
        return wrapper
    return plugin
