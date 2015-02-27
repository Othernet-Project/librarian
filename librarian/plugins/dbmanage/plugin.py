"""
plugin.py: DB management plugin

Backup and rebuild the database.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import time
import logging
import datetime
from os.path import dirname, join

from bottle import view, request, static_file

from ...lib import squery
from ...utils import migrations
from ...lib.archive import process
from ...lib.downloads import get_md5_from_path
from ...lib.i18n import lazy_gettext as _, i18n_path
from ...lib.lock import global_lock, LockFailureError, UnlockFailureError

from ..dashboard import DashboardPlugin
from ..exceptions import NotSupportedError

try:
    from .backup import backup
except RuntimeError:
    raise NotSupportedError('Sqlite3 library not found')


MDIR = join(dirname(dirname(dirname(__file__))), 'migrations')


def get_dbpath():
    return request.app.config['database.path']


def get_backup_dir():
    conf = request.app.config
    backupdir = os.path.join(os.path.normpath(conf['content.filedir']),
                             os.path.normpath(conf['dbmanage.backups']))
    if not os.path.exists(backupdir):
        os.makedirs(backupdir)
    return backupdir


def get_backup_path():
    backupdir = get_backup_dir()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = 'db_backup_%s.sqlite' % timestamp
    return os.path.join(backupdir, filename)


def get_file_url():
    suburl = request.app.config['dbmanage.backups'].replace('\\', '/')
    return i18n_path('/files/%s' % suburl)


def serve_dbfile():
    dbpath = get_dbpath()
    dbdir = os.path.dirname(dbpath)
    dbname = os.path.basename(dbpath)
    return static_file(dbname, root=dbdir, download=True)


def remove_dbfile():
    dbpath = get_dbpath()
    os.unlink(dbpath)
    assert not os.path.exists(dbpath), 'Expected db file to be gone'


def run_migrations():
    db = squery.Database(request.app.config['database.path'])
    migrations.migrate(db, MDIR)
    logging.debug("Finished running migrations")
    return db


def reload_data(db):
    zdir = request.app.config['content.contentdir']
    content = ((get_md5_from_path(f), os.path.join(zdir, f))
               for f in os.listdir(zdir)
               if f.endswith('.zip'))
    res = process(db, content, no_file_ops=True)
    return res[0]


def rebuild():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    start = time.time()
    db = request.db
    logging.debug('Locking database')
    cur = db.acquire_lock()  # should block until everyone else finishes
    logging.debug('Acquiring global lock')
    with global_lock(always_release=True):
        # Now that we have a global lock, we can release the database lock
        cur.execute('ROLLBACK')
        db.disconnect()
        backup(dbpath, bpath)
        remove_dbfile()
        logging.debug('Removed database')
        db = request.db = run_migrations()
        logging.debug('Prepared new database')
        rows = reload_data(db)
        logging.info('Restored metadata for %s pieces of content', rows)
    logging.debug('Released global lock')
    end = time.time()
    return end - start


@view('dbmanage/backup_results', error=None, path=None, time=None)
def perform_backup():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    try:
        btime = backup(dbpath, bpath)
        logging.debug('Database backup took %s seconds', btime)
    except AssertionError as err:
        return dict(error=err.message)
    return dict(path=get_file_url(), time=btime)


@view('dbmanage/rebuild_results', error=None, path=None, time=None, fpath=None)
def perform_rebuild():
    try:
        rtime = rebuild()
    except LockFailureError:
        logging.debug('DBMANAGE: Global lock could not be acquired')
        # Translators, error message displayed when locking fails during
        # database rebuild
        return dict(error=_('Librarian could not enter maintenance mode and '
                            'database rebuild was cancelled. Please make '
                            'sure noone else is using Librarian and '
                            'try again.'))
    return dict(path=i18n_path('/'), time=rtime, fpath=get_file_url())


def install(app, route):
    route('/librarian.sqlite', 'GET', callback=serve_dbfile, no_i18n=True)
    route('/backup', 'POST', callback=perform_backup)
    route('/rebuild', 'POST', callback=perform_rebuild)


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Content database')
    name = 'dbmanage'

    @property
    def dbpath(self):
        return get_dbpath()

    def get_context(self):
        dbpath = self.dbpath
        dbsize = os.stat(dbpath).st_size
        return locals()
