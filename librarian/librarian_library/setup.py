import pytz

from bottle import request

from librarian.librarian_core.contrib.i18n.utils import (set_default_locale,
                                                         get_enabled_locales)
from librarian.librarian_setup.setup import setup_wizard

from .forms import get_language_form, SetupDateTimeForm


def is_language_invalid():
    supervisor = request.app.supervisor
    lang_code = supervisor.exts.setup.get('language')
    return lang_code not in get_enabled_locales()


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='GET', index=1, test=is_language_invalid)
def setup_language_form():
    SetupLanguageForm = get_language_form(request.app.config)
    return dict(form=SetupLanguageForm())


@setup_wizard.register_step('language', template='setup/step_language.tpl',
                            method='POST', index=1, test=is_language_invalid)
def setup_language():
    SetupLanguageForm = get_language_form(request.app.config)
    form = SetupLanguageForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form)

    lang = form.processed_data['language']
    request.app.supervisor.exts.setup.append({'language': lang})
    set_default_locale(lang)
    return dict(successful=True, language=lang)


def has_bad_tz():
    timezone = request.app.supervisor.exts.setup.get('timezone')
    return timezone not in pytz.common_timezones


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
    request.app.supervisor.exts.setup.append({'timezone': timezone})
    return dict(successful=True, timezone=timezone)
