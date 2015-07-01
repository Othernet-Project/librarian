"""
plugin.py: DB management plugin

Backup and rebuild the database.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import time
import logging
import datetime
from os.path import dirname, join

from bottle import request, static_file
from bottle_utils.common import unicode
from bottle_utils.i18n import lazy_ngettext, lazy_gettext as _, i18n_url

from ...core.archive import Archive

from ...lib.lock import global_lock, LockFailureError

from ...utils import migrations, databases
from ...utils.template import view

from ..dashboard import DashboardPlugin
from ..exceptions import NotSupportedError

try:
    from .backup import backup
except RuntimeError:
    raise NotSupportedError('Sqlite3 library not found')


DB_NAME = 'main'
MDIR = join(dirname(dirname(dirname(__file__))), 'migrations', DB_NAME)


def get_dbpath():
    return databases.get_database_path(request.app.config, 'main')


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
    return i18n_url('files:path', path=suburl)


def serve_dbfile():
    dbpath = get_dbpath()
    dbdir = os.path.dirname(dbpath)
    dbname = os.path.basename(dbpath)
    return static_file(dbname, root=dbdir, download=True)


def remove_dbfile():
    dbpath = get_dbpath()
    paths = [dbpath, dbpath + '-wal', dbpath + '-shm']
    for p in paths:
        try:
            os.unlink(p)
        except OSError:
            pass
        finally:
            assert not os.path.exists(p), 'Expected db file to be gone'


def run_migrations(db):
    conf = request.app.config
    migrations.migrate(db, 'librarian.migrations.{0}'.format(DB_NAME), conf)
    logging.debug("Finished running migrations")


def rebuild():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    start = time.time()
    conf = request.app.config
    db = request.db.main
    logging.debug('Locking database')
    db.acquire_lock()
    logging.debug('Acquiring global lock')
    with global_lock(always_release=True):
        db.commit()
        db.close()
        backup(dbpath, bpath)
        remove_dbfile()
        logging.debug('Removed database')
        db.reconnect()
        run_migrations(db)
        logging.debug('Prepared new database')
        archive = Archive.setup(conf['librarian.backend'],
                                db,
                                unpackdir=conf['content.unpackdir'],
                                contentdir=conf['content.contentdir'],
                                spooldir=conf['content.spooldir'],
                                meta_filename=conf['content.metadata'])
        rows = archive.reload_content()
        logging.info('Restored metadata for %s pieces of content', rows)
    request.app.exts.cache.invalidate('content')
    logging.debug('Released global lock')
    end = time.time()
    return end - start


@view('feedback')
def perform_backup():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    try:
        btime = backup(dbpath, bpath)
        logging.debug('Database backup took %s seconds', btime)
    except AssertionError as err:
        # Translators, error message displayed if database backup fails
        base_msg = _('Database backup could not be completed. '
                     'The following error occurred:')
        message = ' '.join(map(unicode, [base_msg, err.message]))
        status = 'error'
        url = i18n_url('dashboard:main')
        # Translators, redirection target if database backup was successful
        target = _('Dashboard')
    else:
        # Translators, message displayed if database backup was successful
        base_msg = _('Database backup has been completed successfully.')
        took_msg = lazy_ngettext('The operation took %s second',
                                 'The operation took %s seconds',
                                 btime) % round(btime, 2)
        message = ' '.join(map(unicode, [base_msg, took_msg]))
        status = 'success'
        url = get_file_url()
        # Translators, redirection target if database backup was successful
        target = _('the backup folder')

    # Translators, used as page title
    title = _('Database backup')
    return dict(status=status,
                page_title=title,
                message=message,
                redirect_url=url,
                redirect_target=target)


@view('feedback')
def perform_rebuild():
    try:
        rtime = rebuild()
    except LockFailureError:
        logging.debug('DBMANAGE: Global lock could not be acquired')
        # Translators, error message displayed if database rebuild fails
        base_msg = _('Database could not be rebuilt. '
                     'The following error occurred:')
        # Translators, error message displayed when locking fails during
        # database rebuild
        reason = _('Librarian could not enter maintenance mode and '
                   'database rebuild was cancelled. Please make '
                   'sure noone else is using Librarian and '
                   'try again.')
        message = ' '.join(map(unicode, [base_msg, reason]))
        status = 'error'
        url = i18n_url('dashboard:main')
        # Translators, redirection target if database backup was successful
        target = _('Dashboard')
    else:
        # Translators, message displayed if database backup was successful
        base_msg = _('Content database has been rebuilt from scratch. A backup'
                     ' copy of the original database has been created. '
                     'You will find it in the files section.')
        # Translators, message displayed if database backup was successful
        took_msg = lazy_ngettext('The operation took %s second',
                                 'The operation took %s seconds',
                                 rtime) % round(rtime, 2)
        message = ' '.join(map(unicode, [base_msg, took_msg]))
        # Translators, message displayed if database backup was successful
        status = 'success'
        url = i18n_url('content:list')
        # Translators, redirection target if database backup was successful
        target = _('Library')

    # Translators, used as page title
    title = _('Database rebuild')
    return dict(status=status,
                page_title=title,
                message=message,
                redirect_url=url,
                redirect_target=target)


def install(app, route):
    route(
        ('download', serve_dbfile, 'GET', '/librarian.sqlite',
         dict(no_i18n=True)),
        ('backup', perform_backup, 'POST', '/backup', {}),
        ('rebuild', perform_rebuild, 'POST', '/rebuild', {}),
    )


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
        return dict(dbpath=dbpath, dbsize=dbsize)
