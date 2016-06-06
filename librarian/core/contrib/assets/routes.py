import os

from bottle import request, static_file, HTTPError
from bottle_utils.lazy import caching_lazy
from streamline import RouteBase


@caching_lazy
def static_root():
    project_root = request.app.config['root']
    static_dir = request.app.config.get('assets.directory', 'static')
    return os.path.join(project_root, static_dir)


@caching_lazy
def static_sources():
    asset_sources = request.app.config.get('assets.sources', {})
    paths, _ = zip(*asset_sources.values())
    return [static_root()] + list(paths)


@caching_lazy
def favicon_path():
    return request.app.config.get('favicon.path', 'favicon.ico')


def send_static(path):
    for static_root in static_sources():
        res = static_file(path, static_root)
        if not isinstance(res, HTTPError):
            break

    return res


class StaticRoute(RouteBase):
    name = 'sys:static'
    path = '/static/<path:path>'
    exclude_plugins = ['session_plugin', 'user_plugin', 'setup_plugin']
    kwargs = dict(no_i18n=True, unlocked=True)

    def get(self, path):
        return send_static(path)


class FaviconRoute(RouteBase):
    name = 'sys:favicon'
    path = '/favicon.ico'
    exclude_plugins = ['session_plugin', 'user_plugin', 'setup_plugin']
    kwargs = dict(no_i18n=True, unlocked=True)

    def get(self, path):
        return send_static(favicon_path())
