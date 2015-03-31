"""
backup.py: SQLite3 backup using online backup API

Code is based on `script by Joongi Kim`_.

.. script by Joongi Kim: https://gist.github.com/achimnol/3021995

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import time
import ctypes
import logging
from ctypes.util import find_library

SQLITE_OK = 0
SQLITE_ERROR = 1
SQLITE_BUSY = 5
SQLITE_LOCKED = 6

SQLITE_OPEN_READONLY = 1
SQLITE_OPEN_READWRITE = 2
SQLITE_OPEN_CREATE = 4

sqlitelib = find_library('sqlite3') or 'libsqlite3.so'
try:
    sqlite = ctypes.CDLL(sqlitelib)
except OSError:
    raise RuntimeError('Sqlite3 library could not be found')

sqlite.sqlite3_backup_init.restype = ctypes.c_void_p


def backup(src, dst):
    p_src_db = ctypes.c_void_p(None)
    p_dst_db = ctypes.c_void_p(None)
    null_ptr = ctypes.c_void_p(None)

    # Open source
    ret = sqlite.sqlite3_open_v2(str(src), ctypes.byref(p_src_db),
                                 SQLITE_OPEN_READONLY, null_ptr)
    # Translators, error message during database backup
    assert ret == SQLITE_OK, 'Opening source database failed'
    assert p_src_db.value is not None, 'Opening source database failed'
    logging.debug("DBMANAGE: opened '%s' as source database", src)

    # Open target
    ret = sqlite.sqlite3_open_v2(str(dst), ctypes.byref(p_dst_db),
                                 SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE,
                                 null_ptr)
    # Translators, error message during database backup
    assert ret == SQLITE_OK, 'Opening backup database failed'
    assert p_dst_db.value is not None, 'Opening backup database failed'
    logging.debug("DBMANAGE: opened '%s' as target database", dst)

    # Create backup handler
    p_backup = sqlite.sqlite3_backup_init(p_dst_db, 'main', p_src_db, 'main')
    assert p_backup is not None, 'Could not create database backup handler'

    # Perform backup
    start = time.time()
    while True:
        ret = sqlite.sqlite3_backup_step(p_backup, 20)
        remaining = sqlite.sqlite3_backup_remaining(p_backup)
        pagecount = sqlite.sqlite3_backup_pagecount(p_backup)
        try:
            progress = (pagecount - remaining) / float(pagecount) * 100
        except ZeroDivisionError:
            progress = 0

        logging.debug('DBMANAGE: backup progress %0.2f%%', progress)
        if remaining == 0:
            break
        if ret in (SQLITE_OK, SQLITE_BUSY, SQLITE_LOCKED):
            logging.debug('Database busy, trying again in 100 seconds')
            sqlite.sqlite3_sleep(100)
    end = time.time()

    sqlite.sqlite3_backup_finish(p_backup)
    sqlite.sqlite3_close(p_dst_db)
    sqlite.sqlite3_close(p_src_db)
    logging.debug("DBMANAGE: backup completed '%s' -> '%s' (took %s seconds)",
                  src, dst, end - start)
    return end - start
