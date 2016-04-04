from bottle import request

from ..system.utils import get_plugin


def set_default_locale(code):
    i18n = get_plugin('i18n')
    i18n.default_locale = code


def set_current_locale(code):
    i18n = get_plugin('i18n')
    i18n.set_locale(code)


def get_enabled_locales(config=None):
    config = config or request.app.supervisor.config
    return config.get('i18n.locales', ['en'])


def is_i18n_enabled(config=None):
    config = config or request.app.supervisor.config
    return config.get('i18n.enabled', False)
