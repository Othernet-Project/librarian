import os

from bottle_utils.i18n import I18NPlugin

from .consts import LANGS


def initialize(supervisor):
    if supervisor.config.get('i18n.enabled'):
        default_locale = supervisor.config.get('i18n.default_locale', 'en')
        domain = supervisor.config.get('i18n.domain')
        locale_dir = os.path.join(
            supervisor.config['root'],
            supervisor.config.get('localedir', 'locales')
        )
        locales = supervisor.config.get('i18n.locales', ['en'])
        langs = [(code, name) for code, name in LANGS if code in locales]
        supervisor.wsgi = I18NPlugin(supervisor.app,
                                     langs=langs,
                                     default_locale=default_locale,
                                     domain=domain,
                                     locale_dir=locale_dir)
