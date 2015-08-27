"""
dashboard.py: dashboard menu item

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from librarian.librarian_menu.menu import MenuItem


class DashboardMenuItem(MenuItem):
    name = 'dashboard'
    label = _("Settings")
    icon_class = 'settings'
    route = 'dashboard:main'
