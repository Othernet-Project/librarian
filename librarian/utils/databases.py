"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


def get_database_configs(conf):
    databases = dict()
    names = conf['database.names']
    for name in names.split(','):
        db_name = name.strip().lower()
        db_path = conf['database.{0}'.format(db_name)]
        databases[db_name] = db_path
    return databases
