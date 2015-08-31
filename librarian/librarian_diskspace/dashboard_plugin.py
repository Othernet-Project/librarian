"""
plugin.py: Diskspace plugin

Display application log on dashboard.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle_utils.i18n import lazy_gettext as _

from librarian.librarian_dashboard.dashboard import DashboardPlugin

from . import zipballs


try:
    os.statvfs
except AttributeError:
    raise RuntimeError("Disk space information not available on this platform")


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Content library stats')
    name = 'diskspace'

    def get_context(self):
        free, total = zipballs.free_space()
        count, used = zipballs.used_space()
        needed = zipballs.needed_space(free)
        return dict(free=free, total=total, count=count, used=used,
                    needed=needed)
