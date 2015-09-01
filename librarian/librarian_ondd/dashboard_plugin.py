"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from librarian.librarian_core.contrib.templates.decorators import template_helper
from librarian.librarian_dashboard.dashboard import DashboardPlugin

from .forms import ONDDForm
from .setup import read_ondd_setup

try:
    from . import ipc
except AttributeError:
    raise RuntimeError('ONDD plugin requires UNIX sockets')


@template_helper
def get_bitrate(status):
    for stream in status.get('streams', []):
        return stream['bitrate']

    return 0


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Tuner settings')
    name = 'ondd'

    def get_context(self):
        initial_data = read_ondd_setup()
        return dict(status=ipc.get_status(),
                    form=ONDDForm(initial_data),
                    files=[])
