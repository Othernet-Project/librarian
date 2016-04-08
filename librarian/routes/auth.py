"""
auth.py: Authentication and ACL handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import i18n_url, lazy_gettext as _
from streamline import RouteBase, XHRPartialFormRoute

from ..core.contrib.auth.users import User
from ..core.contrib.templates.renderer import template
from ..forms.auth import LoginForm, PasswordResetForm
from ..helpers import auth  # NOQA
from ..utils.route_mixins import CSRFRouteMixin, RedirectRouteMixin


class Login(CSRFRouteMixin, RedirectRouteMixin, XHRPartialFormRoute):
    template_func = template
    template_name = 'auth/login'
    partial_template_name = 'auth/_login'
    form_factory = LoginForm

    def form_valid(self):
        self.request.user.options.process('language')
        self.perform_redirect()


class Logout(RedirectRouteMixin, RouteBase):

    def get(self):
        self.request.user.logout()
        self.perform_redirect()
        return ''


class ResetPassword(CSRFRouteMixin, RedirectRouteMixin, XHRPartialFormRoute):
    template_func = template
    template_name = 'auth/reset_password'
    partial_template_name = 'auth/_reset_password'
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
