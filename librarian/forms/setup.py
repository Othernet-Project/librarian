from bottle import request
from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from librarian_core.contrib.i18n.consts import LANGS


def get_default_locale(locales, config):
    def default_locale():
        if request.locale in locales:
            return request.locale
        else:
            return config.get('i18n.default_locale', 'en')
    return default_locale


def get_language_form(config):
    locales = config.get('i18n.locales', ['en'])
    ui_languages = [(code, name) for code, name in LANGS if code in locales]

    class SetupLanguageForm(form.Form):
        # Translators, used as label for language
        language = form.SelectField(_('Language'),
                                    value=get_default_locale(locales, config),
                                    validators=[form.Required()],
                                    choices=ui_languages)

    return SetupLanguageForm
