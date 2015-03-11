"""
sqery.py: Helpers for working with databases

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re
import sqlite3
from functools import wraps
from contextlib import contextmanager

import dateutil.parser
from gevent import spawn
from bottle import request


SLASH = re.compile(r'\\')


sqlite3.register_converter('timestamp', dateutil.parser.parse)


def normurl(url):
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


class Database(object):
    def __init__(self, conn):
        self.conn = conn
        self._cursor = None

    def _convert_query(self, qry):
        """ Ensure any SQLExpression instances are serialized

        :param qry:     raw SQL string or SQLExpression instance
        :returns:       raw SQL string
        """
        if hasattr(qry, '__sqlrepr__'):
            return qry.__sqlrepr__(qry)
        assert isinstance(qry, basestring), 'Expected qry to be string'
        return qry

    def query(self, qry, *params, **kwparams):
        qry = self._convert_query(qry)
        spawn(self.cursor.execute, qry, params or kwparams).join()
        return self.cursor

    def execute(self, qry, *args, **kwargs):
        spawn(self.cursor.execute, qry, *args, **kwargs).join()

    def executemany(self, qry, *args, **kwargs):
        spawn(self.cursor.executemany, qry, *args, **kwargs).join()

    def executescript(self, sql):
        spawn(self.cursor.executescript, sql).join()

    def commit(self):
        spawn(self.conn.commit).join()

    def rollback(self):
        spawn(self.conn.rollback).join()

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
        return spawn(self.cursor.fetchall).get()

    @property
    def result(self):
        return spawn(self.cursor.fetchone).get()

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


def database_plugin(dbpath):
    if hasattr(dbpath, 'cursor'):
        conn = dbpath
    else:
        conn = Database.connect(dbpath)
    def plugin(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            request.db = Database(conn)
            return callback(*args, **kwargs)
        return wrapper
    return plugin
