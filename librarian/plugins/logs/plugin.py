"""
plugin.py: Log plugin

Display application log on dashboard.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request

from ...lib.i18n import lazy_gettext as _

from ..dashboard import DashboardPlugin


def install(app, route):
    pass


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Application logs')
    name = 'logs'

    def get_context(self):
        with open(request.app.config['logging.output'], 'rt') as log:
            logs = ''.join(reversed(list(log)))
        return dict(logs=logs)

