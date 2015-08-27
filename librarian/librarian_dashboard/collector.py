"""
plugins: code related to plugins and plugin loaders

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import os

import bottle

from .exceptions import NotSupportedError

COLLECTED = {}
INSTALLED = {}
DASHBOARD = []


def collect_dashboard_plugin(plugin_name, plugin_mod):
    COLLECTED[plugin_name] = plugin_mod


def route_plugin(app, plugin_name):
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

    :param app:          app for which to create the routing function
    :param plugin_name:  name of the plugin module
    :returns:            routing function
    """
    def _route_plugin(*routes):
        for route in routes:
            name, callback, method, path, kw = route
            name = 'plugins:%s:%s' % (plugin_name, name)
            path = ('/p/%s/' % plugin_name) + path.lstrip('/')
            app.route(path, method, callback, name=name, **kw)
    return _route_plugin


def install_dashboard_plugins(supervisor):
    conf = supervisor.config
    dashboard = conf['dashboard.plugins']

    for name, plugin in COLLECTED.items():
        try:
            plugin.install(supervisor.app, route_plugin(supervisor.app, name))
        except NotSupportedError as err:
            logging.error(
                "Plugin '%s' not supported, skipping (reason: %s)", name,
                err.reason)
            continue
        except AttributeError:
            logging.error("Plugin '%s' not correctly implemented, skipping",
                          name)
            continue

        INSTALLED[name] = plugin
        logging.info('Installed plugin %s', name)

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
