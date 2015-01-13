"""
dashboard.py: routes related to dashboard and configuration management

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from datetime import datetime

import bottle
from bottle import request, view, abort, redirect, default_app, MultiDict

from ..lib import downloads
from ..lib import archive
from ..lib.i18n import lazy_gettext as _, i18n_path
from ..lib.favorites import favorite_content
from ..utils.helpers import hsize
from ..plugins import DASHBOARD as DASHBOARD_PLUGINS

__all__ = ('app', 'dashboard',)


app = default_app()


@view('dashboard')
def dashboard():
    """ Render the dashboard """
    zipballs = downloads.get_zipballs()
    zipballs = list(reversed(downloads.order_zipballs(zipballs)))
    if zipballs:
        last_zip = datetime.fromtimestamp(zipballs[0][1])
        zipballs = len(zipballs)
        logging.debug('Found %s updates' % zipballs)
    else:
        logging.debug('No updates found')
    plugins = DASHBOARD_PLUGINS
    return locals()

