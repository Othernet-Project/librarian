"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import mako_view as view, request, redirect

from ..lib import auth
from ..lib.i18n import lazy_gettext as _


@view('login')
def login():
    if request.method == 'POST':
        next_path = request.forms.get('next', '/')
        username = request.forms.get('username', '')
        password = request.forms.get('password', '')
        if auth.login_user(username, password):
            redirect(next_path)

        return {'username': username,
                'next': next_path,
                # Translators, error message shown on failed login attempt
                'error': _("Please enter the correct username and password.")}

    next_path = request.query.get('next', '/')
    return {'username': '', 'next': next_path, 'error': None}
