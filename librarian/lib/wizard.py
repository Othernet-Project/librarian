"""
wizard.py: Generic form wizard

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, redirect, mako_template as template


class Wizard(object):
    prefix = 'wizard_'

    def __init__(self, name=None, template=None):
        self.name = name
        self.template = template
        self.steps = dict()

    @property
    def id(self):
        return self.prefix + self.name

    def __call__(self, *args, **kwargs):
        if request.method == 'POST':
            return self.process_current_step()

        return self.start_next_step()

    def __next__(self):
        """Return next step of the wizard."""
        wizard_state = request.session.get(self.id)
        if not wizard_state:
            wizard_state = dict(step=0)
        else:
            wizard_state['step'] += 1

        request.session[self.id] = wizard_state
        try:
            return self.steps[wizard_state['step']]
        except KeyError:
            raise StopIteration()

    def start_next_step(self):
        try:
            step = next(self)
        except StopIteration:
            wizard_state = request.session.get(self.id)
            return self.wizard_finished(wizard_state['data'])
        else:
            step_partial = step()
            return template(self.template, step=step_partial)

    def process_current_step(self):
        wizard_state = request.session.get(self.id)
        if not wizard_state:
            redirect(request.fullpath())

        index = wizard_state['step']
        step = self.steps[index]
        step_result = step()
        if isinstance(step_result, basestring):
            # it's a rendered template, the step may have form errors
            return template(self.template, step=step_result)

        current_data = wizard_state.get('data', {})
        current_data[index] = step_result
        wizard_state['data'] = current_data
        request.session[self.id] = wizard_state

        return self.start_next_step()

    def wizard_finished(self, data):
        raise NotImplementedError()

    def register_step(self, index=None):
        def decorator(func):
            idx = max(self.steps.keys() + [-1]) + 1 if index is None else index
            self.steps[idx] = func
            return func
        return decorator
