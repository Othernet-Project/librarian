"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.i18n import i18n_path
from bottle_utils.csrf import csrf_protect, csrf_token, csrf_tag

from ..forms.auth import LoginForm
from ..utils.http import http_redirect
from ..utils.template import view
from ..utils.template_helpers import template_helper


template_helper(csrf_tag)  # register csrf_tag in template_helpers


@template_helper
def is_authenticated():
    return not request.no_auth and request.user.is_authenticated


@view('login')
@csrf_token
def show_login_form():
    return dict(form=LoginForm(), next_path=request.params.get('next', '/'))


@view('login')
@csrf_protect
def login():
    next_path = request.params.get('next', '/')

    form = LoginForm(request.params)
    if form.is_valid():
        return http_redirect(i18n_path(next_path))

    return dict(next_path=next_path, form=form)


def logout():
    next_path = request.params.get('next', '/')
    request.user.logout()
    http_redirect(i18n_path(next_path))


def routes(app):
    return (
        ('auth:login_form', show_login_form, 'GET', '/login/', {}),
        ('auth:login', login, 'POST', '/login/', {}),
        ('auth:logout', logout, 'GET', '/logout/', {}),
    )
