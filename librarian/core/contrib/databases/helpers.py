"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import bottle


POSTGRES_BACKEND = 'postgres'
SQLITE_BACKEND = 'sqlite'
SERVERLESS_DATABASE_BACKENDS = (SQLITE_BACKEND,)


def import_squery(conf):
    backend = conf['database.backend']
    if backend == SQLITE_BACKEND:
        from squery_lite.squery import Database, DatabaseContainer
    elif backend == POSTGRES_BACKEND:
        from squery_pg.squery_pg import Database, DatabaseContainer
    else:
        raise ValueError('Unknown database backend: {}'.format(backend))

    return (Database, DatabaseContainer)


def is_serverless(conf):
    return conf['database.backend'] in SERVERLESS_DATABASE_BACKENDS


def ensure_dir(path):
    """ Make sure directory at path exists """
    if not os.path.exists(path):
        os.makedirs(path)


def get_database_path(conf, name):
    return os.path.abspath(os.path.join(conf['database.path'], name + '.db'))


def get_database_configs(conf):
    serverless = is_serverless(conf)
    databases = dict()
    for pkg_name, db_names in conf['database.sources'].items():
        for name in db_names:
            database = get_database_path(conf, name) if serverless else name
            databases[name] = dict(package_name=pkg_name,
                                   database=database)
    return databases


def get_databases(database_cls, container_cls, db_confs, host, port, user,
                  password, debug=False):
    databases = dict((name,
                      database_cls.connect(host=host,
                                           port=port,
                                           database=db_config['database'],
                                           user=user,
                                           password=password,
                                           debug=debug))
                     for name, db_config in db_confs.items())
    return container_cls(databases, debug=debug)


def init_databases(config):
    (database_cls, container_cls) = import_squery(config)
    database_configs = get_database_configs(config)
    if is_serverless(config):
        # Make sure all necessary directories are present
        for db_config in database_configs.values():
            ensure_dir(os.path.dirname(db_config['database']))

    databases = get_databases(database_cls,
                              container_cls,
                              database_configs,
                              config['database.host'],
                              config['database.port'],
                              config['database.user'],
                              config['database.password'],
                              debug=bottle.DEBUG)
    # Run migrations on all databases
    for db_name, db_config in database_configs.items():
        migration_pkg = '{0}.migrations.{1}'.format(db_config['package_name'],
                                                    db_name)
        database_cls.migrate(databases[db_name], migration_pkg, config)

    return databases


def close_databases(databases):
    for db in databases.values():
        db.close()
