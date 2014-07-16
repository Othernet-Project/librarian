"""
migrations.py: functions for managing migrations

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re
import sqlite3
from functools import wraps
from itertools import dropwhile
from contextlib import contextmanager

__all__ = ('get_migrations', 'get_migration_version', 'run_migration',
           'migrate')


MTABLE = 'migrations'   # SQL table in which migration data is stored
MIGRATION_FILE_RE = re.compile('^\d{2}_[^.]+\.sql$')


def get_migrations(path, min_ver=0):
    """ Get migration files from specified path

    :param path:    path containing migration files
    :param min_ver: minimum migration version
    :returns:       return an iterator that returns only items whose versions
                    are >= min_ver
    """
    int_first_two = lambda s: int(s[:2])

    paths = [(os.path.join(path, f), int_first_two(f))
             for f in os.listdir(path)
             if MIGRATION_FILE_RE.match(f)]
    paths.sort(key=lambda x: x[1])
    return dropwhile(lambda x: x[1] < min_ver, paths)


def get_migration_version(db):
    """ Query database and return migration version

    :param db:  connetion object
    :returns:   current migration version or -1 if no migrations exist
    """
    qry = 'select version from %s where id == 0;' % MTABLE
    try:
        cur = db.query(qry)
    except sqlite3.OperationalError as err:
        if 'no such table' in str(err):
            return -1
        raise
    return cur.fetchone().version


def run_migration(db, path, version):
    """ Run migration script

    :param db:      database connection object
    :param path:    path of the migration script
    :param version: version number of the migration
    """
    with open(path, 'r') as script:
        sql = script.read()
    with db.transaction() as cur:
        cur.executescript(sql)
        qry = 'replace into %s (id, version) values (?, ?)' % MTABLE
        db.query(qry, 0, version)


def migrate(db, path):
    """ Run all migrations that have not been run

    Migrations will be run inside a transaction.

    :param db:      database connection object
    :param path:    path that contains migrations
    """
    ver = get_migration_version(db)
    migrations = get_migrations(path, ver + 1)
    for path, version in migrations:
        run_migration(db, path, version)
        print("Completed migration %s" % version)
