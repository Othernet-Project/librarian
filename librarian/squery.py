"""
sqery.py: Helpers for working with databases

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sqlite3
from functools import wraps
from itertools import dropwhile
from contextlib import contextmanager

from bottle import request

from . import __version__ as _version, __author__ as _author

__version__ = _version
__author__ = _author
__all__ = ('Database', 'database_plugin',)


class Database:
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.db = None
        self._cursor = None

    def connect(self):
        if self.db is None:
            self.db = sqlite3.connect(self.dbpath)

    def disconnect(self):
        if self.db is not None:
            self.db.close()
            self.db = None

    def query(self, qry, *params, **kwparams):
        cursor = self.cursor
        cursor.execute(qry, kwparams or params)
        return cursor

    @property
    def cursor(self):
        self.connect()
        if self._cursor is None:
            self._cursor = self.db.cursor()
        return self._cursor

    @contextmanager
    def transaction(self, silent=False):
        self.cursor.execute('BEGIN')
        try:
            yield self.cursor
            self.db.commit()
        except Exception as err:
            self.db.rollback()
            if silent:
                return
            raise

    def __repr__(self):
        return "<Database dbpath='%s'>" % self.dbpath


def database_plugin(callback):
    @wraps(callback)
    def plugin(*args, **kwargs):
        config = request.app.config
        request.db = db = Database(config['database.path'])
        body = callback(*args, **kwargs)
        db.disconnect()
        return body
    return plugin

