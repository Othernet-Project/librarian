from bottle_utils.i18n import lazy_gettext as _

from ..core.contrib.i18n.consts import LANGS
from ..core.contrib.i18n.utils import set_default_locale
from ..core.exts import ext_container as exts


class LanguageSetting:
    group = 'general'
    verbose_group = _("General settings")
    name = 'default_language'
    label = _("Default language")
    value_type = 'select'
    help_text = _("Interface language that is initially selected for all "
                  "users. Users can change it independently later.")
    required = True

    def __init__(self):
        exts.events.subscribe('SETTINGS_SAVED', self.settings_saved)

    def settings_saved(self, settings):
        set_default_locale(settings['general.default_language'])

    @property
    def default(self):
        return exts.config.get('i18n.default_locale', 'en')

    @property
    def choices(self):
        locales = exts.config.get('i18n.locales', ['en'])
        return [(code, name) for code, name in LANGS if code in locales]

    @property
    def rules(self):
        return dict(name=self.name,
                    group=self.group,
                    label=self.label,
                    value_type=self.value_type,
                    help_text=self.help_text,
                    required=self.required,
                    default=self.default,
                    choices=self.choices)
