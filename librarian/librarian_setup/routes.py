"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request, redirect

from librarian.librarian_core.contrib.templates.renderer import view

from .setup import setup_wizard


TUNER_DEV_PATH = '/dev/dvb/adapter0/frontend0'


def iter_lines(lines):
    while lines:
        yield lines.pop()


@view('diag')
def diag():
    if setup_wizard.is_completed:
        redirect('/')

    logpath = request.app.config['logging.syslog']
    with open(logpath, 'rt') as log:
        logs = iter_lines(list(log)[-100:])

    has_tuner = os.path.exists(TUNER_DEV_PATH)

    return dict(logs=logs, has_tuner=has_tuner)


def exit_wizard():
    next_path = request.params.get('next', '/')
    setup_wizard.exit()
    redirect(next_path)


def routes(app):
    return (
        ('setup:main', setup_wizard, ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', exit_wizard, ['GET'], '/setup/exit/', {}),
        ('setup:diag', diag, 'GET', '/diag/', {}),
    )
