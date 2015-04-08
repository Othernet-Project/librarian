"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os


def get_database_path(conf, name):
    return os.path.join(conf['database.path'], name + '.sqlite')


def get_database_configs(conf):
    databases = dict()
    names = conf['database.names']
    for db_name in names:
        databases[db_name] = get_database_path(conf, db_name)
    return databases
