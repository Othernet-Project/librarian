"""
sqery.py: Helpers for working with databases

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sqlite3
from functools import wraps
from contextlib import contextmanager

from gevent import spawn
from bottle import request
from dateutil.parser import parse


__all__ = ('dbdict', 'Database', 'database_plugin',)


class dbdict(dict):
    """ Dictionary subclass that allows attribute access to items """
    def __init__(self, *args, **kwargs):
        if args:
            super(dbdict, self).__init__(args[0])
        else:
            super(dbdict, self).__init__(kwargs)

    def __getattr__(self, attr):
        return self[attr]


def dbdict_factory(cursor, row):
    """ Convert a row returned from a query into ``dbdict`` objects

    :param cursor:  cursor object
    :param row:     row tuple
    :returns:       row as ``dbdict`` object
    """
    # TODO: Unit tests
    colnames = [d[0] for d in cursor.description]
    return dbdict(dict(zip(colnames, row)))


def convert_timestamp(ts):
    # TODO: Unit tests
    return parse(ts)
sqlite3.register_converter('timestamp', convert_timestamp)


class Database(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.db = None
        self._cursor = None

    def connect(self):
        # TODO: Add unit test for row_factory override
        if self.db is None:
            self.db = spawn(sqlite3.connect, self.dbpath,
                            detect_types=sqlite3.PARSE_DECLTYPES).get()
            self.db.row_factory = dbdict_factory

            # Use atuocommit mode so we can do manual transactions
            self.db.isolation_level = None

    def disconnect(self):
        if self.db is not None:
            spawn(self.db.close).join()
            self.db = None

    def query(self, qry, *params, **kwparams):
        spawn(self.cursor.execute, qry, params or kwparams).join()
        return self.cursor

    def execute(self, qry, params):
        spawn(self.cursor.execute, qry, params).join()

    def executemany(self, qry, params):
        spawn(self.cursor.executemany, qry, params).join()

    def executescript(self, sql):
        spawn(self.cursor.executescript, sql).join()

    def commit(self):
        spawn(self.db.commit).join()

    def rollback(self):
        spawn(self.db.rollback).join()

    def refresh_table_stats(self):
        self.query('ANALYZE sqlite_master;')

    @property
    def cursor(self):
        self.connect()
        if self._cursor is None:
            self._cursor = self.db.cursor()
        return self._cursor

    @property
    def results(self):
        return spawn(self.cursor.fetchall).get()

    @property
    def result(self):
        return spawn(self.cursor.fetchone).get()

    @contextmanager
    def transaction(self, silent=False):
        self.cursor.execute('BEGIN')
        try:
            yield self.cursor
            self.db.commit()
        except Exception:
            self.db.rollback()
            if silent:
                return
            raise

    def acquire_lock(self):
        self.cursor.execute('BEGIN EXCLUSIVE')
        return self.cursor

    def __repr__(self):
        return "<Database dbpath='%s'>" % self.dbpath


def database_plugin(callback):
    @wraps(callback)
    def plugin(*args, **kwargs):
        config = request.app.config
        request.db = db = Database(config['database.path'])
        res = callback(*args, **kwargs)
        spawn(db.disconnect).join()
        return res
    return plugin
