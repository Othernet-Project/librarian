"""
databases.py: Database utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from ...exts import ext_container as exts


def close_databases():
    for db in exts.databases.values():
        db.close()
