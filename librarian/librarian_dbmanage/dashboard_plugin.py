"""
plugin.py: DB management plugin

Backup and rebuild the database.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle_utils.i18n import lazy_gettext as _

from librarian.librarian_dashboard.dashboard import DashboardPlugin

from .dbmanage import get_dbpath


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
