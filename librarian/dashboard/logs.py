"""
plugin.py: Log plugin

Display application log on dashboard.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.i18n import lazy_gettext as _

from librarian_dashboard.dashboard import DashboardPlugin


def iter_lines(lines):
    while lines:
        yield lines.pop()


class LogsDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Application logs')
    name = 'logs'

    def get_context(self):
        logpath = request.app.config['logging.output']
        with open(logpath, 'rt') as log:
            logs = iter_lines(list(log)[-100:])
        return dict(logs=logs)

    def get_template(self):
        return 'logs/dashboard'

