"""
apps.py: apps menu item

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import MenuItem

from bottle_utils.i18n import lazy_gettext as _


class AppsMenuItem(MenuItem):
    label = _("Apps")
    icon_class = 'apps'
    route = 'apps:list'
    group = 'main'
