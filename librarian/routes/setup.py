"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import pytz

from bottle import request, redirect

from ..forms.auth import RegistrationForm
from ..forms.setup import SetupLanguageForm,  SetupDateTimeForm
from ..lib import auth
from ..utils.lang import UI_LOCALES, set_default_locale
from ..utils.setup import setup_wizard


def is_language_invalid():
    return request.app.setup.get('language') not in UI_LOCALES


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='GET', index=1, test=is_language_invalid)
def setup_language_form():
    return dict(form=SetupLanguageForm())


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='POST', index=1, test=is_language_invalid)
def setup_language():
    form = SetupLanguageForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    lang = form.processed_data['language']
    request.app.setup.append({'language': lang})
    set_default_locale(lang)
    return dict(successful=True, language=lang)


def has_bad_tz():
    return request.app.setup.get('timezone') not in pytz.common_timezones


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='GET', index=2, test=has_bad_tz)
def setup_datetime_form():
    return dict(form=SetupDateTimeForm())


@setup_wizard.register_step('datetime', template='setup/step_datetime.tpl',
                            method='POST', index=2, test=has_bad_tz)
def setup_datetime():
    form = SetupDateTimeForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    timezone = form.processed_data['timezone']
    request.app.setup.append({'timezone': timezone})
    return dict(successful=True, timezone=timezone)


def has_no_superuser():
    db = request.db.sessions
    query = db.Select(sets='users', where='is_superuser = ?')
    db.query(query, True)
    return db.result is None


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='GET', index=3, test=has_no_superuser)
def setup_superuser_form():
    return dict(form=RegistrationForm(),
                reset_token=auth.generate_reset_token())


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='POST', index=3, test=has_no_superuser)
def setup_superuser():
    form = RegistrationForm(request.forms)
    reset_token = request.params.get('reset_token')
    if not form.is_valid():
        return dict(successful=False, form=form, reset_token=reset_token)

    auth.create_user(form.processed_data['username'],
                     form.processed_data['password1'],
                     is_superuser=True,
                     db=request.db.sessions,
                     overwrite=True,
                     reset_token=reset_token)
    return dict(successful=True)


def exit_wizard():
    next_path = request.params.get('next', '/')
    request.app.setup.wizard.exit()
    redirect(next_path)


def routes(app):
    return (
        ('setup:main', setup_wizard, ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', exit_wizard, ['GET'], '/setup/exit/', {}),
    )
