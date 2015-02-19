"""
plugin.py: DB management plugin

Backup and rebuild the database.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request, static_file

from ...lib.i18n import lazy_gettext as _, i18n_path

from ..dashboard import DashboardPlugin


def get_dbpath():
    return request.app.config['database.path']


def serve_dbfile():
    dbpath = get_dbpath()
    dbdir = os.path.dirname(dbpath)
    dbname = os.path.basename(dbpath)
    return static_file(dbname, root=dbdir, download=True)


def install(app, route):
    route('librarian.sqlite', ['GET'], callback=serve_dbfile)


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
