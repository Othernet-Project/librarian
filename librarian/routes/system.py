"""
system.py: System routes such as static files and error handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import logging
import datetime
from os.path import dirname, join, basename

from bottle import request, static_file, abort

from librarian import __version__
from ..utils.template import view
from ..utils.template_helpers import template_helper


STATIC_ROOT = join(dirname(dirname(__file__)), 'static')
HASHED_DIR = 'dist'


def symlink_hashed_files_to_unhashed_paths(asset_map):
    for original, hashed in asset_map.items():
        original_path = os.path.join(STATIC_ROOT, original)
        # make sure folder structure is present to hold the symlink
        original_dir = os.path.dirname(original_path)
        if not os.path.exists(original_dir):
            os.makedirs(original_dir)
        # if a previous symlink exists, remove it
        if os.path.exists(original_path) and os.path.islink(original_path):
            os.unlink(original_path)
        # if it still exists, it's not a symlink but a real file so keep it
        if not os.path.exists(original_path):
            hashed_path = os.path.join(STATIC_ROOT, HASHED_DIR, hashed)
            os.symlink(hashed_path, original_path)


def load_asset_map():
    try:
        with open(join(STATIC_ROOT, 'assets.json'), 'r') as assets_file:
            return json.load(assets_file)
    except Exception:
        logging.warning('No hashed assets found.')
        return {}
    else:
        # WORKAROUND: apps api has no access to `static_url` template helper,
        # so if a request comes in with the old unhashed paths, the symlinks
        # with unhased names will point to the hashed files
        symlink_hashed_files_to_unhashed_paths()


ASSET_MAP = load_asset_map()
symlink_hashed_files_to_unhashed_paths(ASSET_MAP)


@template_helper
def static_url(route, path):
    try:
        actual_path = join(HASHED_DIR, ASSET_MAP[path])
    except KeyError:
        actual_path = path

    return request.app.get_url(route, path=actual_path)


def send_static(path):
    return static_file(path, root=STATIC_ROOT)


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
