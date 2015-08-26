"""
setup.py: Device specific librarian configuration

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json
import logging
import os

from bottle import request

from librarian.librarian_core.contrib.templates.renderer import template

from .decorators import AUTO_CONFIGURATORS
from .wizard import Wizard


class Setup(object):

    def __init__(self, setup_file):
        self.setup_file = setup_file
        self.data = self.load()
        if not self.data:
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
        if not os.path.exists(self.setup_file):
            return {}

        try:
            with open(self.setup_file, 'r') as s_file:
                return json.load(s_file)
        except Exception as exc:
            msg = 'Setup file loading failed: {0}'.format(str(exc))
            logging.error(msg)
            return {}

    def append(self, new_data):
        """Save the setup data file."""
        self.data.update(new_data)
        with open(self.setup_file, 'w') as s_file:
            json.dump(self.data, s_file)

    def auto_configure(self):
        data = dict()
        for name, configurator in AUTO_CONFIGURATORS.items():
            data[name] = configurator()
        return data


class SetupWizard(Wizard):
    finished_template = 'setup/finished.tpl'
    allow_override = True
    start_index = 1
    template_func = template

    def __init__(self, *args, **kwargs):
        super(SetupWizard, self).__init__(*args, **kwargs)
        self._is_completed = False

    @property
    def is_completed(self):
        if not self._is_completed:
            self._is_completed = not self.get_needed_steps()
        return self._is_completed

    def wizard_finished(self, data):
        setup_data = dict()
        for step, step_result in data.items():
            setup_data.update(step_result)

        setup = request.app.supervisor.exts.setup
        setup.append(setup_data)
        result = template(self.finished_template, setup=setup)
        return result

    def exit(self):
        # called to clear the state object which stores the steps that were
        # used while stepping through the wizard, after which clicking back
        # won't work anymore
        self.clear_needed_steps()

    def get_next_setup_step_index(self):
        for step_index, step in sorted(self.steps.items(), key=lambda x: x[0]):
            if step['test']():
                return step_index

        return self.step_count + self.start_index

    def override_next_step(self):
        next_setup_step_index = self.get_next_setup_step_index()
        try:
            wanted_step_index = request.params[self.step_param]
        except KeyError:
            self.set_step_index(next_setup_step_index)
            return
        else:
            try:
                wanted_step_index = int(wanted_step_index)
            except ValueError:
                self.set_step_index(next_setup_step_index)
                return
            else:
                if (wanted_step_index not in self.steps or
                        wanted_step_index > next_setup_step_index):
                    self.set_step_index(next_setup_step_index)
                else:
                    self.set_step_index(wanted_step_index)


setup_wizard = SetupWizard(name='setup')
