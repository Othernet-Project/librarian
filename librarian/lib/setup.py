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

from .wizard import Wizard


logger = logging.getLogger(__name__)


class SetupWizard(Wizard):

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)


class Setup(object):

    def __init__(self, setup_file):
        self.setup_file = setup_file
        self.is_completed = False
        self.data = dict()
        self.load()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def load(self):
        """Attempt loading the setup data file."""
        if os.path.exists(self.setup_file):
            with open(self.setup_file, 'r') as s_file:
                try:
                    self.data = json.load(s_file)
                except Exception:
                    logger.exception('Setup file loading failed.')
                else:
                    self.is_completed = True

    def save(self):
        """Save the setup data file."""
        with open(self.setup_file, 'w') as s_file:
            json.dump(self.data, s_file)


def setup_plugin(setup_template):
    setup_wizard.template = setup_template

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            if not request.app.setup.is_completed:
                path = '{0}?next={1}'.format(i18n_url('setup:main'),
                                             request.fullpath())
                return redirect(path)
            return callback(*args, **kwargs)
        return wrapper
    return plugin


setup_wizard = SetupWizard(name='setup')
