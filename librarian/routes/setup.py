"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import platform

import dateutil.parser
import pytz

from bottle import request

from ..forms.auth import RegistrationForm
from ..forms.setup import SetupLanguageForm,  SetupDateTimeForm
from ..lib import auth
from ..lib import wizard
from ..utils.template import template


LINUX = 'Linux'


class SetupWizard(wizard.Wizard):
    finished_template = 'setup/finished.tpl'
    allow_override = True
    start_index = 1
    template_func = template

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
        next_setup_step_index = self.get_next_setup_step_index()
        try:
            wanted_step_index = request.params[self.step_param]
        except KeyError:
            self.set_step_index(next_setup_step_index)
            return
        else:
            try:
                wanted_step_index = int(wanted_step_index)
            except ValueError:
                self.set_step_index(next_setup_step_index)
                return
            else:
                if (wanted_step_index not in self.steps or
                        wanted_step_index > next_setup_step_index):
                    self.set_step_index(next_setup_step_index)
                else:
                    self.set_step_index(wanted_step_index)


setup_wizard = SetupWizard(name='setup')


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='GET', index=1)
def setup_language_form():
    return dict(form=SetupLanguageForm())


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='POST', index=1)
def setup_language():
    form = SetupLanguageForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    lang = form.processed_data['language']
    request.app.setup.append({'language': lang})
    return dict(successful=True, language=lang)


def is_linux():
    return platform.system() == LINUX


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='GET', index=2, test=is_linux)
def setup_datetime_form():
    return dict(form=SetupDateTimeForm())


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='POST', index=2, test=is_linux)
def setup_datetime():
    form = SetupDateTimeForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    timezone = form.processed_data['timezone']
    datetime_str = '{date} {hour}:{minute}'.format(**form.processed_data)
    local_dt = dateutil.parser.parse(datetime_str)
    tz_aware_dt = pytz.timezone(timezone).localize(local_dt)
    # Linux only!
    dt_format = '%Y-%m-%d %T'
    os.system("date +'{0}' -s '{1}'".format(dt_format,
                                            tz_aware_dt.strftime(dt_format)))
    request.app.setup.append({'timezone': timezone, 'datetime': True})
    return dict(successful=True)


def has_no_superuser():
    db = request.db.sessions
    query = db.Select(sets='users', where='is_superuser = ?')
    db.query(query, True)
    return db.result is None


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='GET', index=3, test=has_no_superuser)
def setup_superuser_form():
    return dict(form=RegistrationForm())


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='POST', index=3, test=has_no_superuser)
def setup_superuser():
    form = RegistrationForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    auth.create_user(form.processed_data['username'],
                     form.processed_data['password1'],
                     is_superuser=True,
                     db=request.db.sessions,
                     overwrite=True)
    request.app.setup.append({'superuser': True})
    return dict(successful=True)
