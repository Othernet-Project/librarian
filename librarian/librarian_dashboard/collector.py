"""
plugins: code related to plugins and plugin loaders

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

COLLECTED = {}
DASHBOARD = []


def collect_dashboard_plugin(plugin_cls):
    COLLECTED[plugin_cls.name] = plugin_cls


def install_dashboard_plugins(supervisor):
    conf = supervisor.config
    dashboard = conf['dashboard.plugins']
    # Install dashboard plugins for plugins that have them
    logging.debug("Installing dashboard plugins: %s", ', '.join(dashboard))
    for p in dashboard:
        if p not in COLLECTED:
            logging.debug("Plugin '%s' is not installed, ignoring", p)
            continue
        plugin_cls = COLLECTED[p]
        try:
            DASHBOARD.append(plugin_cls())
            logging.info('Installed dashboard plugin %s', p)
        except AttributeError:
            logging.debug("No dashboard plugin for '%s'", p)
            continue
