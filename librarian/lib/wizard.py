"""
wizard.py: Generic form wizard

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, mako_template as template

from bottle_utils.common import basestring


class MissingStepHandler(ValueError):

    def __init__(self, index, method):
        msg = 'Missing {0} request handler in step: {1}'.format(method, index)
        super(MissingStepHandler, self).__init__(msg)


class Wizard(object):
    valid_methods = ('GET', 'POST')
    prefix = 'wizard_'

    def __init__(self, name=None, template=None):
        self.name = name
        self.template = template
        self.steps = dict()

    def __call__(self, *args, **kwargs):
        # each request gets a separate instance so states won't get mixed up
        instance = self.create_wizard(self.name,
                                      self.template,
                                      self.__dict__)
        return instance.dispatch()

    @property
    def __name__(self):
        return self.__class__.__name__

    def dispatch(self):
        # entry-point of a wizard instance, load wizard state from session
        self.load_state()
        if request.method == 'POST':
            return self.process_current_step()

        return self.start_next_step()

    @property
    def id(self):
        return self.prefix + self.name

    def load_state(self):
        state = request.session.get(self.id)
        if not state:
            state = dict(step=0, data={})
        self.state = state

    def save_state(self):
        request.session[self.id] = self.state

    def next(self):
        """Return next step of the wizard."""
        step_index = self.state['step']
        try:
            step_handlers = self.steps[step_index]
        except KeyError:
            raise StopIteration()
        else:
            try:
                return step_handlers['GET']
            except KeyError:
                raise MissingStepHandler(step_index, 'GET')

    def start_next_step(self):
        try:
            step = next(self)
        except StopIteration:
            return self.wizard_finished(self.state['data'])
        else:
            step_partial = step()
            return template(self.template, step=step_partial)

    def process_current_step(self):
        current_step_index = self.state['step']
        step_handlers = self.steps[current_step_index]
        try:
            step = step_handlers['POST']
        except KeyError:
            raise MissingStepHandler(current_step_index, 'POST')

        step_result = step()
        if isinstance(step_result, basestring):
            # it's a rendered template, the step may have form errors
            return template(self.template, step=step_result)

        self.state['data'][current_step_index] = step_result
        self.state['step'] += 1
        self.save_state()
        return self.start_next_step()

    def wizard_finished(self, data):
        raise NotImplementedError()

    def register_step(self, name, method=valid_methods, index=None):
        def decorator(func):
            next_index = max(self.steps.keys() + [-1]) + 1
            try:
                wanted_index = next_index if index is None else int(index)
                if wanted_index < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValueError('Step index must be a positive integer.')

            if (wanted_index in self.steps and
                    self.steps[wanted_index]['name'] != name):
                # an auto-indexed handler probably have taken the place of this
                # manually indexed handler, switch their places
                self.steps[next_index] = self.steps[wanted_index]
                del self.steps[wanted_index]

            methods = [method] if isinstance(method, basestring) else method
            for method_name in methods:
                if method_name not in self.valid_methods:
                    msg = '{0} is not an acceptable HTTP method.'.format(
                        method_name
                    )
                    raise ValueError(msg)
                self.steps.setdefault(wanted_index, dict(name=name))
                self.steps[wanted_index][method_name] = func

            return func
        return decorator

    def remove_gaps(self):
        """Inplace removal of eventual gaps between registered step indexes."""
        original = [None] * (max(self.steps.keys()) + 1)
        for idx, step in self.steps.items():
            original[idx] = step

        gapless = [step for step in original if step is not None]
        self.steps = dict((idx, step) for idx, step in enumerate(gapless))

    @classmethod
    def create_wizard(cls, name, template, attrs):
        instance = cls(name, template)
        # make sure attributes that were assigned after the wizard instance was
        # created will be passed on to new instances as well
        for name, value in attrs.items():
            setattr(instance, name, value)

        instance.remove_gaps()
        return instance
