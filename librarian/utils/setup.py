"""
setup.py: Device specific librarian configuration

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools
import json
import logging
import os

from bottle import request, redirect
from bottle_utils.i18n import i18n_url


logger = logging.getLogger(__name__)

AUTO_CONFIGURATORS = dict()


def autoconfigure(name):
    """Register functions that will be automatically ran in case a setup file
    was not found. The value these functions return will be associated with the
    passed in `name` parameter, and the resulting pair will be added to the
    setup data."""
    def decorator(func):
        AUTO_CONFIGURATORS[name] = func
        return func
    return decorator


class Setup(object):

    def __init__(self, setup_file):
        self.setup_file = setup_file
        self.data = self.load()
        self.is_completed = self.data is not None and 'completed' in self.data
        if self.data is None:
            self.data = self.auto_configure()

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return self.data.items()

    def load(self):
        """Attempt loading the setup data file."""
        if os.path.exists(self.setup_file):
            with open(self.setup_file, 'r') as s_file:
                try:
                    return json.load(s_file)
                except Exception as exc:
                    msg = 'Setup file loading failed: {0}'.format(str(exc))
                    logger.error(msg)

    def append(self, new_data):
        self.data.update(new_data)
        with open(self.setup_file, 'w') as s_file:
            json.dump(self.data, s_file)

    def save(self, new_data):
        """Save the setup data file."""
        new_data['completed'] = True
        self.append(new_data)
        self.is_completed = True

    def auto_configure(self):
        data = dict()
        for name, configurator in AUTO_CONFIGURATORS.items():
            data[name] = configurator()
        return data


def setup_plugin(setup_path):
    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            if (not request.app.setup.is_completed and
                    request.path != setup_path[len(request.locale) + 1:]):
                return redirect(setup_path)
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'setup'
    return plugin


def load_setup(app):
    # install app-wide access to setup parameters
    app.setup = Setup(app.config['setup.file'])
    # merge setup parameters into app config
    app.config.update(dict(app.setup.items()))


def setup_wizard_plugin(app):
    app.install(setup_plugin(setup_path=i18n_url('setup:main')))
