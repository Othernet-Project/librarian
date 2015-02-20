"""
plugin.py: DB management plugin

Backup and rebuild the database.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import datetime

from bottle import view, request, static_file

from ...lib.i18n import lazy_gettext as _, i18n_path

from ..dashboard import DashboardPlugin
from ..exceptions import NotSupportedError

try:
    from .backup import backup
except RuntimeError:
    raise NotSupportedError('Sqlite3 library not found')


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


@view('dbmanage/backup_results.tpl', error=None, path=None, time=None)
def perform_backup():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    try:
        time = backup(dbpath, bpath)
    except AssertionError as err:
        return dict(error=err.message)
    return dict(path=get_file_url(), time=time)


def install(app, route):
    route('/librarian.sqlite', ['GET'], callback=serve_dbfile, no_i18n=True)
    route('/backup', ['POST'], callback=perform_backup)


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
