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
from bottle_utils.lazy import CachingLazy

from .gspawn import call


SLASH = re.compile(r'\\')


sqlite3.register_converter('timestamp', dateutil.parser.parse)


def sqlarray(n):
    if not n:
        return ''
    if hasattr(n, '__iter__'):
        n = len(n)
    return '({})'.format(', '.join('?' * n))


def sqlin(col, n):
    if not n:
        return ''
    return '{} IN {}'.format(col, sqlarray(n))


class SQL(object):
    def serialize(self):
        raise NotImplementedError('Must be implemented by expression')

    def __repr__(self):
        return self.serialize()


class BaseClause(SQL):
    keyword = None

    def __init__(self, *parts, **kwargs):
        self.parts = list(parts)

    def __len__(self):
        return len(self.parts)

    def __nonzero__(self):
        return len(self.parts) > 0


class Clause(BaseClause):
    keyword = None
    default_connector = None
    null_connector = None

    def __init__(self, *parts, **kwargs):
        connector = kwargs.pop('connector', self.default_connector)
        self.parts = []
        parts = [p for p in parts if p]
        try:
            self.parts.append((None, parts[0]))
        except IndexError:
            return
        for p in parts[1:]:
            self.parts.append((connector, p))

    def serialize_part(self, connector, part):
        if connector:
            part = '{} {}'.format(connector, part)
        return part + ' '

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        for connector, part in self.parts:
            sql += self.serialize_part(connector, part)
        return sql.rstrip()


class From(Clause):
    keyword = 'FROM'
    default_connector = ','

    NATURAL = 'NATURAL'
    INNER = 'INNER'
    CROSS = 'CROSS'
    OUTER = 'OUTER'
    LEFT_OUTER = 'LEFT OUTER'
    JOIN = 'JOIN'

    def __init__(self, *args, **kwargs):
        join = kwargs.pop('join', None)
        if join:
            kwargs['connector'] = '{} JOIN'.format(join)
        super(From, self).__init__(*args, **kwargs)

    def join(self, table, kind=None, natural=False, on=None, using=[]):
        j = []
        if natural:
            j.append(self.NATURAL)
        if kind:
            j.append(kind)
        j.append(self.JOIN)
        if on:
            table += ' ON {}'.format(on)
        elif using:
            if hasattr(using, '__iter__'):
                using = ', '.join(using)
            table += ' USING ({})'.format(using)
        self.parts.append((' '.join(j), table))
        return self

    def inner_join(self, table, natural=False):
        return self.join(table, self.INNER, natural)

    def outer_join(self, table, natural=False):
        return self.join(table, self.OUTER, natural)

    def natural_join(self, table):
        return self.join(table, None, True)


class Where(Clause):
    keyword = 'WHERE'
    default_connector = 'AND'

    AND = 'AND'
    OR = 'OR'

    def __init__(self, *args, **kwargs):
        if kwargs.pop('use_or', False):
            kwargs['connector'] = self.OR
        super(Where, self).__init__(*args, **kwargs)

    def and_(self, condition):
        if not self.parts:
            self.parts.append((None, condition))
        else:
            self.parts.append((self.AND, condition))
        return self

    def or_(self, condition):
        if not self.parts:
            self.parts.append((None, condition))
        else:
            self.parts.append((self.OR, condition))
        return self

    __iand__ = and_
    __iadd__ = and_
    __ior__ = or_


class Group(BaseClause):
    keyword = 'GROUP BY'

    def __init__(self, *parts, **kwargs):
        self.having = kwargs.pop('having', None)
        self.parts = parts

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        sql += ', '.join(self.parts)
        if self.having:
            sql += ' HAVING {}'.format(self.having)
        return sql


class Order(BaseClause):
    keyword = 'ORDER BY'

    def __init__(self, *parts):
        self.parts = list(parts)

    def asc(self, term):
        self.parts.append('+{}'.format(term))
        return self

    def desc(self, term):
        self.parts.append('-{}'.format(term))
        return self

    def __iadd__(self, term):
        return self.asc(term)

    def __isub__(self, term):
        return self.desc(term)

    def _convert_term(self, term):
        if term.startswith('-'):
            return '{} DESC'.format(term[1:])
        elif term.startswith('+'):
            return '{} ASC'.format(term[1:])
        return '{} ASC'.format(term)

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        sql += ', '.join((self._convert_term(t) for t in self.parts))
        return sql


class Limit(SQL):
    def __init__(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset

    def serialize(self):
        if not self.limit:
            return ''
        sql = 'LIMIT {}'.format(self.limit)
        if not self.offset:
            return sql
        sql += ' OFFSET {}'.format(self.offset)
        return sql

    def __len__(self):
        return self.limit

    def __nonzero__(self):
        return self.limit > 0


class Statement(SQL):
    @staticmethod
    def _get_clause(val, sql_class):
        if hasattr(val, 'serialize'):
            return val
        if val is None:
            return sql_class()
        if hasattr(val, '__iter__'):
            return sql_class(*val)
        return sql_class(val)


class Select(Statement):
    def __init__(self, what=['*'], sets=None, where=None, group=None,
                 order=None, limit=None, offset=None):
        self.what = self._get_list(what)
        self.sets = self._get_clause(sets, From)
        self.where = self._get_clause(where, Where)
        self.group = self._get_clause(group, Group)
        self.order = self._get_clause(order, Order)
        self.limit = limit
        self.offset = offset

    def serialize(self):
        sql = 'SELECT '
        sql += ', '.join(self._what)
        if self.sets:
            sql += ' {}'.format(self._from)
        if self.where:
            sql += ' {}'.format(self._where)
        if self.group:
            sql += ' {}'.format(self._group)
        if self.order:
            sql += ' {}'.format(self._order)
        if self.limit:
            sql += ' {}'.format(self._limit)
        return sql + ';'

    @property
    def _what(self):
        return self._get_list(self.what)

    @property
    def _from(self):
        return self._get_clause(self.sets, From)

    @property
    def _where(self):
        return self._get_clause(self.where, Where)

    @property
    def _group(self):
        return self._get_clause(self.group, Group)

    @property
    def _order(self):
        return self._get_clause(self.order, Order)

    @property
    def _limit(self):
        return Limit(self.limit, self.offset)

    @staticmethod
    def _get_list(val):
        if not hasattr(val, '__iter__'):
            return [val]
        return list(val)


class Update(Statement):
    def __init__(self, table, where=None, **kwargs):
        self.table = table
        self.set_args = kwargs
        self.where = self._get_clause(where, Where)

    @property
    def _where(self):
        return self._get_clause(self.where, Where)

    def serialize(self):
        sql = 'UPDATE {} SET '.format(self.table)
        sql += ', '.join(('{} = {}'.format(col, p)
                          for col, p in self.set_args.items()))
        if self.where:
            sql += ' {}'.format(self._where)
        return sql + ';'


class Delete(Statement):
    def __init__(self, table, where=None):
        self.table = table
        self.where = self._get_clause(where, Where)

    def serialize(self):
        sql = 'DELETE FROM {}'.format(self.table)
        if self.where:
            sql += ' {}'.format(self._where)
        return sql + ';'

    @property
    def _where(self):
        return self._get_clause(self.where, Where)


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

    def __getattr__(self, attr):
        return getattr(self._conn, attr)

    def __setattr__(self, attr, value):
        if not hasattr(self, attr) or attr == '_conn':
            object.__setattr__(self, attr, value)
        else:
            setattr(self._conn, attr, value)

    def __repr__(self):
        return "<Connection path='%s'>" % self.path


class Insert(Statement):
    keyword = 'INSERT INTO'

    def __init__(self, table, vals=None, cols=None):
        self.table = table
        self.vals = vals
        self.cols = cols
        if not any([vals, cols]):
            raise ValueError('Either vals or cols must be specified')

    def serialize(self):
        sql = '{} {}'.format(self.keyword, self.table)
        if self.cols:
            sql += ' {}'.format(self._cols)
        sql += ' VALUES {}'.format(self._vals)
        return sql + ';'

    @property
    def _vals(self):
        if not self.vals:
            return self._get_sqlarray((':' + c for c in self.cols))
        return self._get_sqlarray(self.vals)

    @property
    def _cols(self):
        return self._get_sqlarray(self.cols)

    @staticmethod
    def _get_sqlarray(vals):
        if hasattr(vals, '__iter__'):
            return '({})'.format(', '.join(vals))
        if vals.startswith('(') and vals.endswith(')'):
            return vals
        return '({})'.format(vals)


class Replace(Insert):
    keyword = 'REPLACE INTO'


class Database(object):

    # Provide access to query classes for easier access
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
        call(self.conn.commit)

    def refresh_table_stats(self):
        self.execute('ANALYZE sqlite_master;')

    def acquire_lock(self):
        self.execute('BEGIN EXCLUSIVE;')

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
        return call(self.cursor.fetchall)

    @property
    def result(self):
        return call(self.cursor.fetchone)

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


def database_plugin(db_confs, debug=False):
    # Connection objects are held in this closure in a semi-global variable
    # (``connections``) in order to allow reconnection in cases where we need
    # to disconnect temporarily (e.g., when perofrming rebuilds)
    connections = get_connections(db_confs)

    def plugin(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            request.db = DatabaseContainer(connections, debug)
            request.db_connections = connections
            return callback(*args, **kwargs)
        return wrapper
    return plugin
