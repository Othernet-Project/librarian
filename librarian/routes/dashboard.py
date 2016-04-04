"""
dashboard.py: routes related to dashboard and configuration management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request

from librarian_auth.decorators import login_required
from librarian_core.contrib.templates.renderer import view


@login_required()
@view('dashboard/dashboard')
def dashboard():
    """ Render the dashboard """
    return dict(plugins=request.app.supervisor.exts.dashboard.plugins)


def routes(config):
    return (
        ('dashboard:main', dashboard, 'GET', '/dashboard/', {}),
    )
