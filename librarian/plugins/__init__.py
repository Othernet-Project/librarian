"""
plugins: code related to plugins and plugin loaders

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging
import importlib

import bottle
from bottle import default_app

from .exceptions import *

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


def route_plugin(app, name):
    def _route_plugin(path, *args, **kwargs):
        path = ('/p/%s/' % name) + path.lstrip('/')
        app.route(path, *args, **kwargs)
    return _route_plugin


def install_plugins(app):
    plugins = list_plugins()
    conf = app.config
    to_install = [p for p in plugins if conf.get('plugins.%s' % p) == 'yes']
    dashboard = [p.strip().lower()
                 for p in conf.get('dashboard.plugins', '').split(',')]

    # Import each plugin module and initialize it
    for mod in to_install:
        plugin = __import__('librarian.plugins.%s.plugin' % mod,
                            fromlist=['plugin'])

        try:
            plugin.install(app, route_plugin(app, mod))
        except NotSupportedError:
            logging.debug('Plugin %s is not supported. Skipping.', mod)

        INSTALLED[mod] = plugin
        logging.debug('Installed plugin %s', mod)

    # Install dashboard plugins for plugins that have them
    for p in dashboard:
        if p not in INSTALLED:
            continue
        plugin = INSTALLED[p]
        try:
            DASHBOARD.append(plugin.Dashboard())
        except AttributeError:
            logging.debug('No dashboard plugin for %s', p)
            continue

