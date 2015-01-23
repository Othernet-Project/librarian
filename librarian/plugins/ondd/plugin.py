"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from ...lib.i18n import lazy_gettext as _

from ..exceptions import NotSupportedError
from ..dashboard import DashboardPlugin

from . import ipc


def install(app, route):
    import socket
    try:
        socket.AF_UNIX
    except AttributeError:
        raise NotSupportedError('ONDD plugin requires UNIX sockets')


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Tuner settings')
    name = 'ondd'

    def get_context(self):
        status = ipc.get_status()
        return dict(status=status)

