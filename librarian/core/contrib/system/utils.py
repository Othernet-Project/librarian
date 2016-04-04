from bottle import request


def get_plugin(name):
    for plugin in request.app.plugins:
        if getattr(plugin, 'name', '') == name:
            return plugin
