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
from ..lib.setup import setup_wizard
from ..utils.lang import UI_LOCALES, DEFAULT_LOCALE


DATETIME_KEYS = ('year', 'month', 'day', 'hour', 'minute', 'second')
MONTHS = [(idx, name) for idx, name in enumerate(calendar.month_name)]


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


@setup_wizard.register_step('datetime', method='GET', index=1)
def setup_datetime_form():
    now = datetime.datetime.now()
    current_dt = dict((key, getattr(now, key)) for key in DATETIME_KEYS)
    return template('setup/step_datetime.tpl',
                    errors={},
                    months=MONTHS,
                    datetime=current_dt)


@setup_wizard.register_step('datetime', method='POST', index=1)
def setup_datetime():
    datetime_template = '{year}-{month}-{day} {hour}:{minute}:{second}'
    entered_dt = dict((key, request.forms.get(key, ''))
                      for key in DATETIME_KEYS)
    datetime_str = datetime_template.format(**entered_dt)
    try:
        parse_datetime(datetime_str)
    except ValueError as exc:
        errors = {'_': str(exc)}
        return template('setup/step_datetime.tpl',
                        errors=errors,
                        months=MONTHS,
                        datetime=entered_dt)
    except TypeError:
        errors = {'_': _("Please select a valid date and time.")}
        return template('setup/step_datetime.tpl',
                        errors=errors,
                        months=MONTHS,
                        datetime=entered_dt)

    # Linux only!
    os.system("date +'%Y-%m-%d %T' -s '{0}'".format(datetime_str))
    return {}


@setup_wizard.register_step('superuser', method='GET', index=2)
def setup_superuser_form():
    return template('setup/step_superuser.tpl', errors={})


@setup_wizard.register_step('superuser', method='POST', index=2)
def setup_superuser():
    username = request.forms.get('username')
    password1 = request.forms.get('password1')
    password2 = request.forms.get('password2')
    if password1 != password2:
        errors = {'_': _("The entered passwords do not match.")}
        return template('setup/step_superuser.tpl', errors=errors)

    try:
        auth.create_user(username,
                         password1,
                         is_superuser=True,
                         db=request.db.sessions)
    except auth.UserAlreadyExists:
        errors = {'username': _("This username is already taken.")}
        return template('setup/step_superuser.tpl', errors=errors)
    except auth.InvalidUserCredentials:
        errors = {'_': _("Invalid user credentials, please try again.")}
        return template('setup/step_superuser.tpl', errors=errors)

    return {}
