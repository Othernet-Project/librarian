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

from bottle import request, redirect, mako_template as template

from bottle_utils.i18n import i18n_url

from .wizard import Wizard


logger = logging.getLogger(__name__)

AUTO_CONFIGURATORS = dict()


def autoconfigurator(name):
    def decorator(func):
        AUTO_CONFIGURATORS[name] = func
        return func
    return decorator


class SetupWizard(Wizard):

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)

        request.app.setup.save(setup_data)
        result = template(self.finished_template)
        return result


class Setup(object):

    def __init__(self, setup_file):
        self.setup_file = setup_file
        self.data = self.load()
        self.is_completed = self.data is not None
        if not self.is_completed:
            self.data = self.auto_configure()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def load(self):
        """Attempt loading the setup data file."""
        if os.path.exists(self.setup_file):
            with open(self.setup_file, 'r') as s_file:
                try:
                    return json.load(s_file)
                except Exception:
                    logger.exception('Setup file loading failed.')

    def save(self, new_data):
        """Save the setup data file."""
        self.data.update(new_data)
        with open(self.setup_file, 'w') as s_file:
            json.dump(self.data, s_file)
        self.is_completed = True

    def auto_configure(self):
        data = dict()
        for name, configurator in AUTO_CONFIGURATORS.items():
            data[name] = configurator()
        return data


def setup_plugin(setup_template, setup_finished_template):
    setup_wizard.template = setup_template
    setup_wizard.finished_template = setup_finished_template

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            setup_path = i18n_url('setup:main')[len(request.locale) + 1:]
            if (not request.app.setup.is_completed and
                    request.path != setup_path):
                path = '{0}?next={1}'.format(setup_path, request.fullpath)
                return redirect(path)
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'setup'
    return plugin


setup_wizard = SetupWizard(name='setup')
