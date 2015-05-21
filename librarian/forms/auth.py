"""
auth.py: Authentication forms

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from ..lib import auth
from ..lib import forms


class LoginForm(forms.Form):
    # Translators, used as label for a login field
    username = forms.StringField(_("Username"),
                                 placeholder=_('username'),
                                 validators=[forms.Required()])
    # Translators, used as label for a password field
    password = forms.PasswordField(_("Password"),
                                   placeholder=_('password'),
                                   validators=[forms.Required()])

    def validate(self):
        username = self.processed_data['username']
        password = self.processed_data['password']

        if not auth.login_user(username, password):
            message = _("Please enter the correct username and password.")
            raise forms.ValidationError(message, {})
