import os

from bottle import request, static_file, HTTPError
from bottle_utils.lazy import caching_lazy


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


def send_static(path):
    for static_root in static_sources():
        res = static_file(path, static_root)
        if not isinstance(res, HTTPError):
            break

    return res


@caching_lazy
def favicon_path():
    return request.app.config.get('favicon.path', 'favicon.ico')


def send_favicon():
    return send_static(favicon_path())


def routes(config):
    skip_plugins = config['app.skip_plugins']
    return (
        ('sys:static', send_static,
         'GET', '/static/<path:path>',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
        ('sys:favicon', send_favicon,
         'GET', '/favicon.ico',
         dict(no_i18n=True, unlocked=True, skip=skip_plugins)),
    )
