"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle_utils.i18n import i18n_url, lazy_gettext as _
from streamline import RouteBase, XHRPartialFormRoute

from ..core.contrib.auth.users import User
from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..forms.auth import LoginForm, PasswordResetForm, EmergencyResetForm
from ..helpers import auth  # NOQA
from ..utils.route_mixins import CSRFRouteMixin, RedirectRouteMixin


class Login(CSRFRouteMixin, RedirectRouteMixin, XHRPartialFormRoute):
    path = '/login/'
    template_func = template
    template_name = 'auth/login'
    partial_template_name = 'auth/_login'
    form_factory = LoginForm

    def form_valid(self):
        self.request.user.options.process('language')
        self.perform_redirect()


class Logout(RedirectRouteMixin, RouteBase):
    path = '/logout/'

    def get(self):
        self.request.user.logout()
        self.perform_redirect()
        return ''


class PasswordReset(CSRFRouteMixin, RedirectRouteMixin, XHRPartialFormRoute):
    path = '/reset-password/'
    template_func = template
    template_name = 'auth/password_reset'
    partial_template_name = 'auth/_password_reset'
    form_factory = PasswordResetForm

    def form_valid(self):
        username = self.form.processed_data['username']
        User.set_password(username, self.form.processed_data['password1'])
        if self.request.user.is_authenticated:
            self.request.user.logout()
        login_url = self.add_next_parameter(i18n_url('auth:login'))
        body = template('ui/feedback.tpl',
                        # Translators, used as page title on feedback page
                        page_title=_('New password was set'),
                        # Translators, used as link label on feedback page in
                        # "You will be taken to log-in page..."
                        redirect_target=_('log-in page'),
                        # Translators, shown after password has been changed
                        message=_("Password for username '{username}' has "
                                  "been set.").format(username=username),
                        status='success',
                        redirect_url=login_url)
        return self.HTTPResponse(body=body)


class EmergencyReset(CSRFRouteMixin, RedirectRouteMixin, XHRPartialFormRoute):
    path = '/emergency/'
    template_func = template
    template_name = 'auth/emergency_reset'
    partial_template_name = 'auth/_emergency_reset'
    form_factory = EmergencyResetForm
    exclude_plugins = ['sessions']

    def read_token_file(self):
        token_path = self.config.get('emergency.file', '')
        if not os.path.isfile(token_path):
            # Not configured or missing emergency reset token file
            return self.abort(404)

        with open(token_path, 'r') as f:
            token = f.read()
            if not token.strip():
                # Token file is empty, so treat it as missing token file
                return self.abort(404)

        return token

    def get_reset_token(self):
        if self.request.method.lower() == 'get':
            return User.generate_reset_token()
        return self.request.params.get('reset_token')

    def clear_auth_databases(self):
        dbs = exts.databases
        dbs.auth.execute(dbs.auth.Delete('users'))
        dbs.sessions.execute(dbs.sessions.Delete('sessions'))

    def recreate_user(self, username, password):
        return User.create(username,
                           password,
                           is_superuser=True,
                           db=exts.databases.librarian,
                           reset_token=self.get_reset_token())

    def get_context(self):
        ctx = super(EmergencyReset, self).get_context()
        ctx.update(reset_token=self.get_reset_token())
        return ctx

    def get(self):
        self.read_token_file()
        # If user is already logged in, redirect to password reset page
        # There's no need to do anything heavy-handed in this case.
        if self.request.user.is_authenticated:
            return self.redirect(i18n_url('auth:password_reset'))
        return super(EmergencyReset, self).get()

    def form_valid(self):
        self.clear_auth_databases()
        username = self.form.processed_data['username']
        password = self.form.processed_data['password1']
        self.recreate_user(username, password)
        body = template('ui/feedback.tpl',
                        # Translators, used as page title on feedback page
                        page_title=_('Emergency reset successful'),
                        # Translators, used as link label on feedback page in
                        # "You will be taken to log-in page..."
                        redirect_target=_('log-in page'),
                        # Translators, shown after emergency reset
                        message=_("You may now log in as "
                                  "'{username}'.").format(username=username),
                        status='success',
                        redirect_url=i18n_url('auth:login'))
        return self.HTTPResponse(body=body)
