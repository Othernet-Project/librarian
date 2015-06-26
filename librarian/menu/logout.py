"""
logout.py: logout menu item

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import MenuItem

from bottle import request
from bottle_utils.i18n import i18n_url, lazy_gettext as _


class LogoutMenuItem(MenuItem):
    label = _("Log out")
    icon_class = 'logout'
    route = 'auth:logout'

    def is_visible(self):
        return hasattr(request, 'user') and request.user.is_authenticated

    def get_path(self):
        return i18n_url(self.route) + '?next=' + request.fullpath
