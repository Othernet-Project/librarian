"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from .exceptions import ConfigurationFormatError


def get_database_configs(conf):
    databases = dict()
    try:
        names = conf['database.names']
        path = conf['database.path']
    except KeyError as err:
        raise ConfigurationFormatError(err)

    for name in names.split(','):
        db_name = name.strip().lower()
        db_path = os.path.join(os.path.normpath(path), db_name)
        databases[db_name] = db_path
    return databases
