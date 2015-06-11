"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import os

import bottle

from ..lib import squery

from .migrations import migrate
from .system import ensure_dir


def get_database_path(conf, name):
    return os.path.join(conf['database.path'], name + '.sqlite')


def get_database_configs(conf):
    databases = dict()
    names = conf['database.names']
    for db_name in names:
        databases[db_name] = get_database_path(conf, db_name)
    return databases


def apply_migrations(app):
    database_configs = get_database_configs(app.config)
    for db_name, db_path in database_configs.items():
        logging.debug('Using database {}'.format(db_path))

    # Make sure all necessary directories are present
    for db_path in database_configs.values():
        ensure_dir(os.path.dirname(db_path))

    # Run database migrations
    app.databases = squery.get_databases(database_configs, debug=bottle.DEBUG)
    for db_name, db in app.databases.items():
        migrate(db,
                'librarian.migrations.{0}'.format(db_name),
                app.config)


def close_databases(app):
    for db in app.databases.values():
        db.close()


def database_plugin(app):
    app.install(squery.database_plugin(app.databases))
