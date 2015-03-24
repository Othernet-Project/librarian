"""
dashboard.py: routes related to dashboard and configuration management

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import view, default_app

from ..plugins import DASHBOARD as DASHBOARD_PLUGINS

__all__ = ('app', 'dashboard',)


app = default_app()


@view('dashboard')
def dashboard():
    """ Render the dashboard """
    plugins = DASHBOARD_PLUGINS
    return locals()

