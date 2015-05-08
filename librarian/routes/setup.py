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

import pytz
from bottle import request, mako_template as template
from bottle_utils.i18n import lazy_gettext as _
from dateutil.parser import parse as parse_datetime

from ..lib import auth
from ..lib import wizard
from ..utils.lang import UI_LOCALES, DEFAULT_LOCALE


DATETIME_KEYS = ('date', 'hour', 'minute')
MONTHS = [(idx, idx) for idx, nm in enumerate(calendar.month_name) if idx > 0]
HOURS = [(i, i) for i in range(24)]
MINUTES = [(i, str(i).zfill(2)) for i in range(60)]
TIMEZONES = [(tzname, tzname) for tzname in pytz.common_timezones]
DEFAULT_TIMEZONE = pytz.common_timezones[0]

DATE_CONSTS = dict(months=MONTHS,
                   hours=HOURS,
                   minutes=MINUTES,
                   timezones=TIMEZONES)


class SetupWizard(wizard.Wizard):
    finished_template = 'setup/finished.tpl'
    allow_override = True
    start_index = 1

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)

        request.app.setup.save(setup_data)
        result = template(self.finished_template, setup=request.app.setup)
        return result

    def get_next_setup_step_index(self):
        for step_index, step in sorted(self.steps.items(), key=lambda x: x[0]):
            try:
                request.app.setup[step['name']]
            except KeyError:
                return step_index

        return self.step_count + self.start_index

    def override_next_step(self):
        try:
            wanted_step_index = int(request.params.get(self.step_param, ''))
        except ValueError:
            return
        else:
            if wanted_step_index not in self.steps:
                return

        next_setup_step_index = self.get_next_setup_step_index()
        if wanted_step_index > next_setup_step_index:
            self.set_step_index(next_setup_step_index)
        else:
            self.set_step_index(wanted_step_index)


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

    request.app.setup.append({'language': lang})
    return dict(successful=True, language=lang)


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='GET', index=2)
def setup_datetime_form():
    now = datetime.datetime.now()
    date = '{0:04d}-{1:02d}-{2:02d}'.format(now.year, now.month, now.day)
    current_dt = dict(date=date, hour=now.hour, minute=now.minute)
    return dict(errors={},
                datetime=current_dt,
                tz=DEFAULT_TIMEZONE,
                **DATE_CONSTS)


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='POST', index=2)
def setup_datetime():
    datetime_template = '{date} {hour}:{minute}'
    entered_dt = dict((key, request.forms.get(key, ''))
                      for key in DATETIME_KEYS)
    datetime_str = datetime_template.format(**entered_dt)

    tz_id = request.forms.get('timezone')
    if tz_id not in pytz.all_timezones:
        errors = {'timezone': _("Please select a valid timezone.")}
        return dict(successful=False,
                    errors=errors,
                    datetime=entered_dt,
                    tz=tz_id,
                    **DATE_CONSTS)
    try:
        local_dt = parse_datetime(datetime_str)
    except ValueError as exc:
        errors = {'_': str(exc)}
        return dict(successful=False,
                    errors=errors,
                    datetime=entered_dt,
                    tz=tz_id,
                    **DATE_CONSTS)
    except TypeError:
        errors = {'_': _("Please select a valid date and time.")}
        return dict(successful=False,
                    errors=errors,
                    datetime=entered_dt,
                    tz=tz_id,
                    **DATE_CONSTS)

    tz_aware_dt = pytz.timezone(tz_id).localize(local_dt)
    # Linux only!
    dt_format = '%Y-%m-%d %T'
    os.system("date +'{0}' -s '{1}'".format(dt_format,
                                            tz_aware_dt.strftime(dt_format)))
    request.app.setup.append({'timezone': tz_id, 'datetime': True})
    return dict(successful=True)


def has_no_superuser():
    db = request.db.sessions
    query = db.Select(sets='users', where='is_superuser = ?')
    db.query(query, True)
    return db.result is None


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='GET', index=3, test=has_no_superuser)
def setup_superuser_form():
    return dict(errors={}, username='')


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='POST', index=3, test=has_no_superuser)
def setup_superuser():
    username = request.forms.get('username')
    password1 = request.forms.get('password1')
    password2 = request.forms.get('password2')
    if password1 != password2:
        errors = {'_': _("The entered passwords do not match.")}
        return dict(successful=False, errors=errors, username=username)

    try:
        auth.create_user(username,
                         password1,
                         is_superuser=True,
                         db=request.db.sessions,
                         overwrite=True)
    except auth.UserAlreadyExists:
        errors = {'username': _("This username is already taken.")}
        return dict(successful=False, errors=errors, username='')
    except auth.InvalidUserCredentials:
        errors = {'_': _("Invalid user credentials, please try again.")}
        return dict(successful=False, errors=errors, username=username)

    request.app.setup.append({'superuser': True})
    return dict(successful=True)
