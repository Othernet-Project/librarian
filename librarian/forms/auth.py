"""
auth.py: Authentication forms

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import hashlib

from bottle import request

from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from ..lib import auth


class TokenValidator(form.Validator):
    messages = {
        # Translators, errorm essage shown when emergency reset token is
        # invalid
        'bad_token': _('This emergency reset token is invalid'),
    }

    def validate(self, v):
        if not v:
            return
        config = request.app.config
        emergency_token_path = config.get('emergency.file')
        if not os.path.isfile(emergency_token_path):
            raise form.ValidationError('bad_token', {'value': ''})
        with open(emergency_token_path, 'r') as f:
            emergency_token = f.read().strip()
        if not emergency_token:
            raise form.ValidationError('bad_token', {'value': ''})
        if self.to_token(v.strip().lower()) != emergency_token:
            raise form.ValidationError('bad_token', {'value': ''})

    @staticmethod
    def to_token(s):
        """ Convert clear-text to hashed token """
        sha256 = hashlib.sha256()
        sha256.update(s.encode('utf8'))
        return sha256.hexdigest()


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


class PasswordResetForm(form.Form):
    messages = {
        'password_match': _("The entered passwords do not match."),
        'invalid_token': _('Password reset token does not match any user'),
    }
    # Translators, used as label in create user form
    reset_token = form.StringField(_("Password reset token"),
                                   validators=[form.Required()],
                                   placeholder='123456')
    # Translators, used as label in password reset form
    password1 = form.PasswordField(_("Password"),
                                   validators=[form.Required()],
                                   placeholder=_('password'))
    # Translators, used as label in password reset form
    password2 = form.PasswordField(_("Confirm Password"),
                                   validators=[form.Required()],
                                   placeholder=_('confirm password'))

    def validate(self):
        password1 = self.processed_data['password1']
        password2 = self.processed_data['password2']
        if password1 != password2:
            raise form.ValidationError('password_match', {})


class EmergencyResetForm(RegistrationForm):
    messages = {
        'registration_error': _("The entered passwords do not match."),
        # Translators, used as error message for emergency reset token form
        # field
        'bad_token': _('Invalid emergency reset token'),
    }

    # Translators, used as label for emergency reset token field
    emergency_reset = form.StringField(_('Emergency reset token'),
                                       validators=[form.Required(),
                                                   TokenValidator()],
                                       placeholder='12345678')
