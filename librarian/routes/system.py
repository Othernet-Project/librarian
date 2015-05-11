"""
system.py: System routes such as static files and error handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json
import logging
import datetime
from os.path import dirname, join, basename

from bottle import mako_view as view, request, static_file, abort

from librarian import __version__
from ..utils.template_helpers import template_helper


STATICDIR = join(dirname(dirname(__file__)), 'static')
HASHEDDIR = 'dist'
try:
    with open(join(STATICDIR, 'assets.json'), 'r') as assets_file:
        ASSET_MAPPING = json.load(assets_file)
except Exception:
    logging.warning('No hashed assets found.')
    ASSET_MAPPING = {}


@template_helper
def static_url(route, path):
    try:
        actual_path = join(HASHEDDIR, ASSET_MAPPING[path])
    except KeyError:
        actual_path = path

    return request.app.get_url(route, path=actual_path)


def send_static(path):
    # WORKAROUND: apps api has no access to `static_url` template helper, so if
    # a request comes in with the old unhashed paths, return a file to them
    try:
        actual_path = join(HASHEDDIR, ASSET_MAPPING[path])
    except KeyError:
        actual_path = path
    # END WORKAROUND
    return static_file(actual_path, root=STATICDIR)


def send_favicon():
    return send_static('img/favicon.ico')


def send_logfile():
    conf = request.app.config
    log_path = conf['logging.output']
    log_dir = dirname(log_path)
    filename = basename(log_path)
    new_filename = datetime.datetime.now().strftime(
        'librarian_%%s_%Y-%m-%d_%H-%M-%S.log') % __version__
    return static_file(filename, root=log_dir, download=new_filename)


@view('500')
def show_error_page(exc):
    logging.error("Unhandled error '%s' at %s %s:\n\n%s",
                  exc.exception,
                  request.method.upper(),
                  request.path,
                  exc.traceback)
    return dict(trace=exc.traceback)


@view('503')
def show_maint_page(exc):
    return dict()


@view('404')
def show_page_missing(exc):
    print(exc)
    return dict()


@view('403')
def show_access_denied_page():
    return dict()


def all_404(path):
    abort(404)
