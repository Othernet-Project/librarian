"""
migrations.py: functions for managing migrations

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re
import sys
import sqlite3
import logging
import importlib


MTABLE = 'migrations'   # SQL table in which migration data is stored
VERSION_SQL = 'select version from %s where id == 0;' % MTABLE
REPLACE_SQL = 'replace into %s (id, version) values (0, ?);' % MTABLE
MIGRATION_TABLE_SQL = """
create table %s
(
    id primary_key unique default 0,
    version integer null
);
""" % MTABLE
MIGRATION_FILE_RE = re.compile('^\d{2}_[^.]+\.sql$')
PYMOD_RE = re.compile(r'^\d+_[^.]+\.pyc?$', re.I)


def get_mods(package):
    """ List all loadable python modules in a directory

    This function looks inside the specified directory for all files that look
    like Python modules with a numeric prefix and returns them. It will omit
    any duplicates and return file names without extension.

    :param package: package object
    :returns:       generator containing file names without extension
    """
    pkgdir = package.__path__[0]
    unique = set(os.path.splitext(f)[0] for f in os.listdir(pkgdir)
                 if PYMOD_RE.match(f))
    return sorted(list(unique))


def get_new(modules, min_ver=0):
    """ Get list of migrations that haven't been run yet

    :param modules: iterable containing module names
    :param min_ver: minimum migration version
    :returns:       return an iterator that returns only items whose versions
                    are >= min_ver
    """
    int_first_two = lambda s: int(s[:2])
    modules = ((f, int_first_two(f)) for f in modules)
    modules = sorted(modules, key=lambda x: x[1])
    for mod in modules:
        if mod[1] < min_ver:
            continue
        yield mod


def load_mod(module, package):
    """ Load a module named ``module`` from given search``path``

    The module path prefix is set according to the ``prefix`` argument.
    By defualt the module is loaded as if it comes from a global
    'db_migrations' package.  As such, it may conflict with any 'db_migration'
    package. The module can be looked up in ``sys.modules`` as
    ``db_migration.MODNAME`` where ``MODNAME`` is the name supplied as
    ``module`` argument. Keep in mind that relative imports from within the
    module depend on this prefix.

    This function raises an ``ImportError`` exception if module is not found.

    :param module:  name of the module to load
    :param package: package object
    :returns:       module object
    """
    name = '%s.%s' % (package.__name__, module)
    if name in sys.modules:
        return sys.modules[name]
    return importlib.import_module(name, package=package.__name__)


def get_version(db):
    """ Query database and return migration version

    :param db:  connetion object
    :returns:   current migration version or -1 if no migrations exist
    """
    try:
        db.query(VERSION_SQL)
    except sqlite3.OperationalError as err:
        if 'no such table' in str(err):
            db.query(MIGRATION_TABLE_SQL)
            db.query(REPLACE_SQL, 0)
            return 0
        raise
    return db.result.version


def run_migration(version, db, mod, conf={}):
    """ Run migration script

    :param version: version number of the migration
    :param db:      database connection object
    :param path:    path of the migration script
    :param conf:    application configuration (if any)
    """
    with db.transaction():
        mod.up(db, conf)
        db.query(REPLACE_SQL, version)


def migrate(db, package, conf={}):
    """ Run all migrations that have not been run

    Migrations will be run inside a transaction.

    :param db:              database connection object
    :param package:         package that contains the migrations
    :param conf:            application configuration object
    """
    ver = get_version(db)
    package = importlib.import_module(package)
    logging.debug('Migration version for %s is %s', package.__package__, ver)
    mods = get_mods(package)
    migrations = get_new(mods, ver + 1)
    for name, version in migrations:
        mod = load_mod(name, package)
        run_migration(version, db, mod, conf)
        logging.debug("Finished migrating to %s", name)
    db.refresh_table_stats()
