"""
apps.py: routes related to apps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat
import logging

from fdsend import send_file
from bottle import request, mako_view as view, abort

from ..core import apps


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
        metadata, content = apps.extract_file(app_path, path, no_read=True)
    except KeyError as err:
        logging.error("<%s> Coult not extract '%s': %s", app_path, path, err)
        abort(404)
    filename = os.path.basename(path)
    return send_file(content, filename, metadata.file_size,
                     os.stat(app_path)[stat.ST_MTIME])
