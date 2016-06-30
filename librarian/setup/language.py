from bottle import request

from ..core.contrib.i18n.utils import (set_default_locale,
                                       set_current_locale,
                                       get_enabled_locales)
from ..forms.setup import get_language_form


class LanguageStep:
    name = 'language'
    index = 10
    template = 'setup/step_language.tpl'

    @staticmethod
    def test():
        supervisor = request.app.supervisor
        lang_code = supervisor.exts.setup.get('language')
        return lang_code not in get_enabled_locales()

    @staticmethod
    def get():
        SetupLanguageForm = get_language_form(request.app.config)
        return dict(form=SetupLanguageForm())

    @staticmethod
    def post():
        SetupLanguageForm = get_language_form(request.app.config)
        form = SetupLanguageForm(request.forms)
        if not form.is_valid():
            return dict(successful=False, form=form)

        lang = form.processed_data['language']
        request.app.supervisor.exts.setup.append({'language': lang})
        set_default_locale(lang)
        set_current_locale(lang)
        return dict(successful=True, language=lang)
