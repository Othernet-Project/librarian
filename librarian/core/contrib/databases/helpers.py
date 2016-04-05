"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import bottle

from squery_pg.squery_pg import Database

from ...exts import ext_container as exts


POSTGRES_BACKEND = 'postgres'
SQLITE_BACKEND = 'sqlite'
PATHS_CONFIGURABLE = (SQLITE_BACKEND,)


def is_path_configurable():
    return exts.config['database.backend'] in PATHS_CONFIGURABLE


def get_database_path(basepath, name):
    return os.path.abspath(os.path.join(basepath, name + '.db'))


def ensure_dir(path):
    """ Make sure directory at path exists """
    if not os.path.exists(path):
        os.makedirs(path)


def register_database(name, pkg_name, basepath=None):
    params = dict(host=exts.config['database.host'],
                  port=exts.config['database.port'],
                  database=name,
                  user=exts.config['database.user'],
                  password=exts.config['database.password'],
                  debug=bottle.DEBUG)
    if basepath:
        params['path'] = get_database_path(basepath, name)
    db = Database.connect(**params)
    db.package_name = pkg_name
    exts.databases[name] = db


def run_migrations():
    path_configurable = is_path_configurable()
    # Run migrations on all databases
    for (db_name, db) in exts.databases.items():
        # Make sure all necessary directories are present
        if path_configurable:
            ensure_dir(os.path.dirname(db.path))
        migration_pkg = '{0}.migrations.{1}'.format(db.package_name, db_name)
        db.migrate(db, migration_pkg, exts.config)


def close_databases():
    for db in exts.databases.values():
        db.close()
