"""
plugins: code related to plugins and plugin loaders

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging

import bottle
from bottle import static_file

from .exceptions import NotSupportedError

PLUGINS_PATH = os.path.dirname(__file__)
INSTALLED = {}
DASHBOARD = []


def is_pkg(path):
    init = os.path.join(path, '__init__.py')
    return os.path.isdir(path) and os.path.isfile(init)


def list_plugins():
    plugins = []
    for p in os.listdir(PLUGINS_PATH):
        pkgdir = os.path.join(PLUGINS_PATH, p)
        if not is_pkg(pkgdir):
            continue
        plugins.append(p)
    return plugins


def route_plugin(app, mod):
    """ Return a function for routing plugin routes

    The route information must be in the following format::

        (name, callback,
         method, path, route_configuration)

    The path is always prefixed with ``/p/module_name/``. For instance, if your
    route has a path of ``/bar``, and is called ``foo``, it will be remapped to
    ``/p/foo/bar``.

    Similarily to paths, names are also modified. The ``plugins:`` prefix. For
    a plugin module ``foo`` and route name of ``bar``, we therefore get a full
    route name that spells ``plugins:foo:bar``.

    :param app:     app for which to create the routing function
    :param mod:     name of the plugin module
    :returns:       routing function
    """
    def _route_plugin(*routes):
        for route in routes:
            name, callback, method, path, kw = route
            name = 'plugins:%s:%s' % (mod, name)
            path = ('/p/%s/' % mod) + path.lstrip('/')
            app.route(path, method, callback, name=name, **kw)
    return _route_plugin


def install_views(mod):
    """ Add view lookup path if plugin has views directory

    :param mod:  module name
    """
    view_path = os.path.join(PLUGINS_PATH, mod, 'views')
    if not os.path.isdir(view_path):
        return
    bottle.TEMPLATE_PATH.insert(1, view_path)


def install_static(app, mod):
    """ Add routes for plugin static if plugin contains a static directory

    All routes are mapped to urls that start with ``/s/`` prefix followed by
    module name. So, for a plugin called ``foo``, we get ``js/main.js`` asset
    by using the following path: ``/s/foo/js/main.js``.

    Each route is also given a name with ``plugins:`` prefix and ``:static``
    suffix added to the module name. Fof a module called ``foo``, the route
    name is ``plugins:foo:static``.

    :param app:  application object
    :param mod:  module name
    """
    static_path = os.path.join(PLUGINS_PATH, mod, 'static')
    if not os.path.isdir(static_path):
        return

    def _route_plugin_static(path):
        return static_file(path, static_path)
    _route_plugin_static.__name__ = '_route_%s_static' % mod

    app.route('/s/%s/<path:path>' % mod, 'GET',
              _route_plugin_static,
              name='plugins:%s:static' % mod,
              no_i18n=True,
              skip=app.config['librarian.skip_plugins'])


def install_plugins(app):
    plugins = list_plugins()
    conf = app.config
    to_install = [p for p in plugins if conf.get('plugins.%s' % p, False)]
    dashboard = conf['dashboard.plugins']

    # Import each plugin module and initialize it
    for mod in to_install:
        try:
            plugin = __import__('librarian.plugins.%s.plugin' % mod,
                                fromlist=['plugin'])
            logging.debug("Plugin '%s' loaded", mod)
        except ImportError as err:
            logging.error("Plugin '%s' could not be loaded, skipping (reason: "
                          "%s)", mod, err)
            continue
        except NotSupportedError as err:
            logging.error(
                "Plugin '%s' not supported, skipping (reason: %s)", mod,
                err.reason)
            continue

        try:
            plugin.install(app, route_plugin(app, mod))
        except NotSupportedError as err:
            logging.error(
                "Plugin '%s' not supported, skipping (reason: %s)", mod,
                err.reason)
            continue
        except AttributeError:
            logging.error("Plugin '%s' not correctly implemented, skipping",
                          mod)
            continue

        install_views(mod)
        install_static(app, mod)

        INSTALLED[mod] = plugin
        logging.info('Installed plugin %s', mod)

    # Install dashboard plugins for plugins that have them
    logging.debug("Installing dashboard plugins: %s", ', '.join(dashboard))
    for p in dashboard:
        if p not in INSTALLED:
            logging.debug("Plugin '%s' is not installed, ignoring", p)
            continue
        plugin = INSTALLED[p]
        try:
            DASHBOARD.append(plugin.Dashboard())
            logging.info('Installed dashboard plugin %s', p)
        except AttributeError:
            logging.debug("No dashboard plugin for '%s'", p)
            continue
