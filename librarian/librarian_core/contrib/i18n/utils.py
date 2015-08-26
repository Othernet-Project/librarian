from bottle import request


def set_default_locale(code):
    for plugin in request.app.plugins:
        if getattr(plugin, 'name', '') == 'i18n':
            plugin.default_locale = code


def get_enabled_locales():
    return request.app.supervisor.config.get('i18n.locales', ['en'])
