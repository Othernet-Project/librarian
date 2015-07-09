"""
system.py: System routes such as static files and error handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import datetime

from os.path import abspath, dirname, join, basename, splitext

from bottle import request, static_file, abort

from librarian import __version__
from ..utils.template import view


STATIC_ROOT = join(dirname(dirname(abspath(__file__))), 'static')


def send_static(path):
    return static_file(path, root=STATIC_ROOT)


def send_favicon():
    return send_static('img/favicon.ico')


def send_logfile(log_path):
    log_dir = dirname(log_path)
    filename = basename(log_path)
    (name, ext) = splitext(filename)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    params = dict(name=name, version=__version__, timestamp=timestamp, ext=ext)
    new_filename = '{name}_{version}_{timestamp}{ext}'.format(**params)
    return static_file(filename, root=log_dir, download=new_filename)


def send_librarian_log():
    log_path = request.app.config['logging.output']
    return send_logfile(log_path)


def send_syslog():
    log_path = request.app.config['logging.syslog']
    return send_logfile(log_path)


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
def show_access_denied_page(exc):
    return dict()


def all_404(path):
    abort(404)


def routes(app):
    skip_plugins = app.config['librarian.skip_plugins']

    app.error(403)(show_access_denied_page)
    app.error(404)(show_page_missing)
    app.error(500)(show_error_page)
    app.error(503)(show_maint_page)

    return (
        ('sys:static', send_static,
         'GET', '/static/<path:path>',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:favicon', send_favicon,
         'GET', '/favicon.ico',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:librarian_log', send_librarian_log,
         'GET', '/librarian.log',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:syslog', send_syslog,
         'GET', '/syslog',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        # This route handler is added because unhandled missing pages cause
        # bottle to _not_ install any plugins, and some are essential to
        # rendering of the 404 page (e.g., i18n, sessions, auth).
        ('sys:all404', all_404,
         ['GET', 'POST'], '/<path:path>', dict()),
    )
