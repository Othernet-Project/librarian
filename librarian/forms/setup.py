"""
setup.py: Setup wizard forms

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from ..lib import forms
from ..utils.lang import UI_LANGS, DEFAULT_LOCALE


class SetupLanguageForm(forms.Form):
    # Translators, used as label for language
    language = forms.SelectField(_('Language'),
                                 value=DEFAULT_LOCALE,
                                 validators=[forms.Required()],
                                 choices=UI_LANGS)
