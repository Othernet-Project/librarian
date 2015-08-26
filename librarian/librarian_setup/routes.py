"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, redirect

from .setup import setup_wizard


def exit_wizard():
    next_path = request.params.get('next', '/')
    setup_wizard.exit()
    redirect(next_path)


def routes(app):
    return (
        ('setup:main', setup_wizard, ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', exit_wizard, ['GET'], '/setup/exit/', {}),
    )
