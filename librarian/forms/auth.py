"""
auth.py: Authentication forms

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from ..lib import auth


class LoginForm(form.Form):
    messages = {
        'login_error': _("Please enter the correct username and password.")
    }
    # Translators, used as label for a login field
    username = form.StringField(_("Username"),
                                placeholder=_('username'),
                                validators=[form.Required()])
    # Translators, used as label for a password field
    password = form.PasswordField(_("Password"),
                                  placeholder=_('password'),
                                  validators=[form.Required()])

    def validate(self):
        username = self.processed_data['username']
        password = self.processed_data['password']

        if not auth.login_user(username, password):
            raise form.ValidationError('login_error', {})


class RegistrationForm(form.Form):
    messages = {
        'registration_error': _("The entered passwords do not match.")
    }
    # Translators, used as label in create user form
    username = form.StringField(_("Username"),
                                validators=[form.Required()],
                                placeholder=_('username'))
    # Translators, used as label in create user form
    password1 = form.PasswordField(_("Password"),
                                   validators=[form.Required()],
                                   placeholder=_('password'))
    # Translators, used as label in create user form
    password2 = form.PasswordField(_("Confirm Password"),
                                   validators=[form.Required()],
                                   placeholder=_('confirm password'))

    def validate(self):
        password1 = self.processed_data['password1']
        password2 = self.processed_data['password2']
        if password1 != password2:
            raise form.ValidationError('registration_error', {})
