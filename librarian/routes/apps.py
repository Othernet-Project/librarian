"""
apps.py: routes related to apps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging

from fdsend import send_file
from bottle import request, abort

from ..core import apps
from ..core import zipballs
from ..utils.template import view


PREFIX = '/apps'


@view('app_list')
def show_apps():
    appdir = request.app.config['content.appdir']
    apps_found = []
    if os.path.exists(appdir):
        for path in os.listdir(appdir):
            path = os.path.join(appdir, path)
            if os.path.isfile(path) and path.endswith('.zip'):
                try:
                    apps_found.append(apps.get_app_info(path))
                except apps.MetadataError as err:
                    # Skip this app
                    logging.error('<%s> Could not decode app metadata: %s',
                                  path, err)
                    pass
    return dict(apps=apps_found)


def send_app_file(appid, path='index.html'):
    appdir = request.app.config['content.appdir']
    app_path = os.path.join(appdir, appid + '.zip')
    if path.startswith('/'):
        path = path[1:]
    if not os.path.exists(appdir):
        abort(404)
    try:
        content = zipballs.get_file(app_path, path)
    except zipballs.ValidationError as exc:
        logging.error("<{0}> Coult not extract '{1}': {2}".format(app_path,
                                                                  path,
                                                                  exc))
        abort(404)
    else:
        filename = os.path.basename(path)
        timestamp = os.stat(app_path).st_mtime
        content_file = zipballs.StringIO(content)
        return send_file(content_file, filename, len(content), timestamp)


def routes(app):
    return (
        ('apps:list', show_apps,
         'GET', '/apps/', dict(unlocked=True)),
        ('apps:app', send_app_file,
         'GET', '/apps/<appid>/', dict(unlocked=True)),
        ('apps:asset', send_app_file,
         'GET', '/apps/<appid>/<path:path>', dict(unlocked=True)),
    )
