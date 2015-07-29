"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.html import set_qparam
from bottle_utils.form import ValidationError
from bottle_utils.csrf import csrf_protect, csrf_token, csrf_tag
from bottle_utils.i18n import i18n_path, i18n_url, lazy_gettext as _

from ..forms.auth import LoginForm, PasswordResetForm
from ..lib.auth import get_user_by_reset_token, set_password
from ..utils.template import view, template
from ..utils.http import http_redirect
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


@view('reset_password')
@csrf_token
def show_reset_form():
    next_path = request.params.get('next', '/')
    return dict(next_path=next_path, form=PasswordResetForm())


@view('reset_password')
@csrf_token
def reset():
    next_path = request.params.get('next', '/')
    form = PasswordResetForm(request.params)
    if request.user.is_authenticated:
        # Set arbitrary non-empty value to prevent form error. We don't really
        # care about this field otherwise.
        form.reset_token.bind_value('not needed')
    if not form.is_valid():
        return dict(next_path=next_path, form=form)
    if request.user.is_authenticated:
        username = request.user.username
    else:
        user = get_user_by_reset_token(form.processed_data['reset_token'])
        if not user:
            form._error = ValidationError('invalid_token', {'value': ''})
            return dict(next_path=next_path, form=form)
        username = user.username
    set_password(username, form.processed_data['password1'])
    if request.user.is_authenticated:
        request.user.logout()
    login_url = i18n_url('auth:login_form') + set_qparam(
        next=next_path).to_qs()
    return template('feedback.tpl',
                    # Translators, used as page title on feedback page
                    page_title=_('New password was set'),
                    # Translators, used as link label on feedback page in "You
                    # will be taken to log-in page..."
                    redirect_target=_('log-in page'),
                    # Translators, shown after password has been changed
                    message=_("Password for username '%(username)s' has been "
                              "set.") % {'username': username},
                    status='success',
                    redirect_url=login_url)


def routes(app):
    return (
        ('auth:login_form', show_login_form, 'GET', '/login/', {}),
        ('auth:login', login, 'POST', '/login/', {}),
        ('auth:logout', logout, 'GET', '/logout/', {}),
        ('auth:reset_form', show_reset_form, 'GET', '/reset-password/', {}),
        ('auth:reset', reset, 'POST', '/reset-password/', {}),
    )
