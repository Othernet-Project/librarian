"""
plugin.py: Settings plugin

Manage librarian settings.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.i18n import lazy_gettext as _

from librarian_dashboard.dashboard import DashboardPlugin


class SettingsDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Settings')
    name = 'settings'

    def get_template(self):
        return '{}/dashboard'.format(self.name)

    def get_context(self):
        settings = request.app.supervisor.exts.settings
        form_cls = settings.get_form()
        return dict(form=form_cls(),
                    groups=settings.groups)

