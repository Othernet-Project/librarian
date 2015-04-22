"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, mako_template as template

from bottle_utils.i18n import lazy_gettext as _

from ..lib.setup import setup_wizard
from ..utils.lang import UI_LOCALES, DEFAULT_LOCALE


@setup_wizard.register_step('language', method='GET', index=0)
def setup_language_form():
    return template('setup/step_language.tpl',
                    errors={},
                    language={'language': DEFAULT_LOCALE})


@setup_wizard.register_step('language', method='POST', index=0)
def setup_language():
    lang = request.forms.get('language')
    if lang not in UI_LOCALES:
        errors = {'language': _('Please select a valid language.')}
        return template('setup/step_language.tpl',
                        errors=errors,
                        language={'language': DEFAULT_LOCALE})

    return {'language': lang}
