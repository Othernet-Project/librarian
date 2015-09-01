"""
diag.py: Diagnostic page

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import redirect, request
from bottle_utils.i18n import i18n_url

from ..utils.setup import setup_wizard
from ..utils.template import view


TUNER_DEV_PATH = '/dev/dvb/adapter0/frontend0'


def iter_lines(lines):
    while lines:
        yield lines.pop()


@view('diag')
def diag():
    if setup_wizard.is_completed:
        redirect(i18n_url('content:list'))

    logpath = request.app.config['logging.syslog']
    with open(logpath, 'rt') as log:
        logs = iter_lines(list(log)[-100:])

    has_tuner = os.path.exists(TUNER_DEV_PATH)

    return dict(logs=logs, has_tuner=has_tuner)


def routes(app):
    return (
        ('diag:main', diag, 'GET', '/diag/', {}),
    )
