import os

from bottle_utils.i18n import I18NPlugin

from ...exts import ext_container as exts
from .consts import LANGS


def i18n_middleware(app):
    default_locale = exts.config.get('i18n.default_locale', 'en')
    domain = exts.config.get('i18n.domain')
    locale_dir = os.path.join(exts.config['root'],
                              exts.config.get('localedir', 'locales'))
    locales = exts.config.get('i18n.locales', ['en'])
    langs = [(code, name) for code, name in LANGS if code in locales]
    return I18NPlugin(app,
                      langs=langs,
                      default_locale=default_locale,
                      domain=domain,
                      locale_dir=locale_dir)
