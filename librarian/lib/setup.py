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
steps = []


class Setup(object):

    def __init__(self, setup_file):
        self.is_completed = False
        self._load(setup_file)

    def _load(self, setup_file):
        """Attempt loading the setup config file."""
        if os.path.exists(setup_file):
            with open(setup_file, 'r') as config_file:
                try:
                    self.config = json.load(config_file)
                except Exception:
                    logger.exception('Setup config loading failed.')
                else:
                    self.is_completed = True

    def get_next_step(self):
        """Return next step of the setup wizard."""
        setup_state = request.session.get('setup')
        if not setup_state:
            setup_state = dict(step=0)
        else:
            setup_state['step'] += 1

        request.session['setup'] = setup_state
        return steps[setup_state['step']]

    def store(self, data):
        """Called by individual steps to add their data to the so far collected
        data by all steps of the wizard."""
        setup_state = request.session.get('setup')
        setup_state['data'].update(data)
        request.session['setup'] = setup_state


def register_wizard_step(index=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        if index is None:
            steps.append(wrapper)
        else:
            steps.insert(index, wrapper)
        return wrapper
    return decorator


def setup_step_dispatcher_route():
    step = request.setup.get_next_step()
    return step()


def setup_plugin(app, setup_file):
    app.setup = Setup(setup_file)

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            if not request.app.setup.is_completed:
                return redirect(i18n_url('setup:main'))
            return callback(*args, **kwargs)
        return wrapper
    return plugin
