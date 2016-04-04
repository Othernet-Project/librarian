"""
plugin.py: Diskspace plugin

Display application log on dashboard.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request
from bottle_utils.i18n import lazy_gettext as _

from librarian_dashboard.dashboard import DashboardPlugin

from . import storage
from .tasks import check_diskspace


try:
    os.statvfs
except AttributeError:
    raise RuntimeError("Disk space information not available on this platform")


class DiskspaceDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Storage devices')
    name = 'diskspace'

    def get_template(self):
        return self.name + '/dashboard.tpl'

    def get_context(self):
        supervisor = request.app.supervisor
        check_diskspace(supervisor)
        return dict(storages=storage.get_content_storages(),
                    active_storage_id=storage.get_consoildate_status())
