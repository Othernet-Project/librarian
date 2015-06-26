"""
updates.py: updates menu item

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import MenuItem

from bottle_utils.i18n import lazy_gettext as _

from ..utils.core_helpers import filter_downloads


class UpdatesMenuItem(MenuItem):
    icon_class = 'updates'
    route = 'downloads:list'

    def _updates(self):
        return len(filter_downloads(lang=None))

    def is_visible(self):
        return self._updates() > 0

    @property
    def label(self):
        update_count = self._updates()
        if update_count > 99:
            update_count = '!'
        lbl = _("Updates")
        if update_count > 0:
            lbl += ' <span class="count">{0}</span>'.format(update_count)
        return lbl
