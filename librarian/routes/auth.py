"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import mako_view as view, request
from bottle_utils.i18n import lazy_gettext as _, i18n_path

from ..lib import auth
from ..lib.validate import nonempty
from ..utils.http import http_redirect


@view('login', vals={}, errors={})
def show_login_form():
    return dict(next_path=request.params.get('next', '/'))


@view('login')
def login():
    errors = {}
    next_path = request.forms.get('next', '/')

    # Translators, error message shown when user does not supply username
    username = nonempty('username', _('Type in your username'), errors, True)

    # Translators, error message shown when user does not supply password
    password = nonempty('password', _('Type in your password'), errors)

    if errors:
        return dict(next_path=next_path, errors=errors, vals=request.forms)

    if not auth.login_user(username, password):
        errors['_'] = _("Please enter the correct username and password.")
        return dict(next_path=next_path, errors=errors, vals=request.forms)

    return http_redirect(i18n_path(next_path))


def logout():
    next_path = request.params.get('next', '/')
    request.user.logout()
    http_redirect(i18n_path(next_path))
