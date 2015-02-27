"""
system.py: System routes such as static files and error handlers

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import datetime
from os.path import dirname, join, basename

from bottle import view, request, static_file


STATICDIR = join(dirname(dirname(__file__)), 'static')


def send_static(path):
    return static_file(path, root=STATICDIR)


def send_logfile():
    conf = request.app.config
    log_path = conf['logging.output']
    dirname = dirname(log_path)
    filename = basename(log_path)
    new_filename = datetime.datetime.now().strftime(
        'librarian_%%s_%Y-%m-%d_%H-%M-%S.log') % __version__
    return static_file(filename, root=dirname, download=new_filename)


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
