"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import calendar
import datetime
import os

from bottle import request, mako_template as template
from bottle_utils.i18n import lazy_gettext as _
from dateutil.parser import parse as parse_datetime

from ..lib import auth
from ..lib import wizard
from ..utils.lang import UI_LOCALES, DEFAULT_LOCALE


DATETIME_KEYS = ('year', 'month', 'day', 'hour', 'minute', 'second')
MONTHS = [(idx, name) for idx, name in enumerate(calendar.month_name)]


class SetupWizard(wizard.Wizard):
    finished_template = 'setup/finished.tpl'
    allow_back = True
    start_index = 1

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)

        request.app.setup.save(setup_data)
        result = template(self.finished_template, setup=setup_data)
        return result


setup_wizard = SetupWizard(name='setup')


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='GET', index=1)
def setup_language_form():
    return dict(errors={}, language={'language': DEFAULT_LOCALE})


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='POST', index=1)
def setup_language():
    lang = request.forms.get('language')
    if lang not in UI_LOCALES:
        errors = {'language': _('Please select a valid language.')}
        return dict(successful=False,
                    errors=errors,
                    language={'language': DEFAULT_LOCALE})

    return dict(successful=True, language=lang)


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='GET', index=2)
def setup_datetime_form():
    now = datetime.datetime.now()
    current_dt = dict((key, getattr(now, key)) for key in DATETIME_KEYS)
    return dict(errors={}, months=MONTHS, datetime=current_dt)


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='POST', index=2)
def setup_datetime():
    datetime_template = '{year}-{month}-{day} {hour}:{minute}:{second}'
    entered_dt = dict((key, request.forms.get(key, ''))
                      for key in DATETIME_KEYS)
    datetime_str = datetime_template.format(**entered_dt)
    try:
        parse_datetime(datetime_str)
    except ValueError as exc:
        errors = {'_': str(exc)}
        return dict(successful=False,
                    errors=errors,
                    months=MONTHS,
                    datetime=entered_dt)
    except TypeError:
        errors = {'_': _("Please select a valid date and time.")}
        return dict(successful=False,
                    errors=errors,
                    months=MONTHS,
                    datetime=entered_dt)

    # Linux only!
    os.system("date +'%Y-%m-%d %T' -s '{0}'".format(datetime_str))
    return dict(successful=True)


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='GET', index=3)
def setup_superuser_form():
    return dict(errors={})


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='POST', index=3)
def setup_superuser():
    username = request.forms.get('username')
    password1 = request.forms.get('password1')
    password2 = request.forms.get('password2')
    if password1 != password2:
        errors = {'_': _("The entered passwords do not match.")}
        return dict(successful=False, errors=errors)

    try:
        auth.create_user(username,
                         password1,
                         is_superuser=True,
                         db=request.db.sessions)
    except auth.UserAlreadyExists:
        errors = {'username': _("This username is already taken.")}
        return dict(successful=False, errors=errors)
    except auth.InvalidUserCredentials:
        errors = {'_': _("Invalid user credentials, please try again.")}
        return dict(successful=False, errors=errors)

    return dict(successful=True)
