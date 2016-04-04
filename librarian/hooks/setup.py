import importlib

from bottle_utils.i18n import lazy_gettext as _

from librarian_core.contrib.i18n.consts import LANGS
from librarian_core.contrib.i18n.utils import set_default_locale

from .setup import Setup, SetupWizard
from .steps import setup_language, setup_language_form, is_language_invalid


def component_member_loaded(supervisor, member, config):
    mod_path = '{0}.setup'.format(member['pkg_name'])
    try:
        importlib.import_module(mod_path)  # they autoregister themselves
    except ImportError:
        pass  # no setup wizard steps in this component


def settings_saved(settings):
    set_default_locale(settings['general.default_language'])


def initialize(supervisor):
    # install app-wide access to setup parameters
    supervisor.exts.setup = Setup(supervisor)
    setup_wizard = SetupWizard(name='setup')
    supervisor.exts.setup_wizard = setup_wizard
    setup_wizard.register('language',
                          setup_language_form,
                          template='setup/step_language.tpl',
                          method='GET',
                          index=1,
                          test=is_language_invalid)
    setup_wizard.register('language',
                          setup_language,
                          template='setup/step_language.tpl',
                          method='POST',
                          index=1,
                          test=is_language_invalid)
    # register option to change default language
    default_language = supervisor.config.get('i18n.default_locale', 'en')
    locales = supervisor.config.get('i18n.locales', ['en'])
    ui_languages = [(code, name) for code, name in LANGS if code in locales]
    help_text = _("Interface language that is initially selected for all "
                  "users. Users can change it independently later.")
    supervisor.exts.settings.add_group('general', _("General settings"))
    supervisor.exts.settings.add_field(name='default_language',
                                       group='general',
                                       label=_("Default language"),
                                       value_type='select',
                                       help_text=help_text,
                                       required=True,
                                       default=default_language,
                                       choices=ui_languages)
    # register handler that sets default language when settings are saved
    supervisor.exts.events.subscribe('SETTINGS_SAVED', settings_saved)
