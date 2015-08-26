"""
wizard.py: Generic form wizard

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, redirect, template

from bottle_utils.common import basestring


class MissingStepHandler(ValueError):

    def __init__(self, index, method):
        msg = 'Missing {0} request handler in step: {1}'.format(method, index)
        super(MissingStepHandler, self).__init__(msg)


class Wizard(object):
    valid_methods = ('GET', 'POST')
    prefix = 'wizard_'
    step_param = 'step'
    start_index = 0
    allow_override = False
    template_func = template

    def __init__(self, name):
        self.name = name
        self.state = None
        self.steps = dict()

    def __call__(self, *args, **kwargs):
        # each request gets a separate instance so states won't get mixed up
        instance = self.create_wizard(self.name, self.__dict__)
        return instance.dispatch()

    @property
    def __name__(self):
        return self.__class__.__name__

    def dispatch(self):
        # entry-point of a wizard instance, load wizard state from session
        created = self.load_state()
        currently_needed_steps = self.get_needed_steps()
        if created:
            needed_steps = self.state['needed_steps'] = currently_needed_steps
        else:
            needed_steps = self.state['needed_steps']
            needed_steps += [idx for idx in currently_needed_steps
                             if idx not in needed_steps]

        self.skip_needless_steps(needed_steps)
        self.remove_gaps()
        self.override_next_step()

        if request.method == 'POST':
            return self.process_current_step()

        return self.start_next_step()

    @property
    def id(self):
        return self.prefix + self.name

    @property
    def step_count(self):
        return len(self.steps)

    @property
    def current_step_index(self):
        return self.state['step']

    def set_step_index(self, step_index):
        self.state['step'] = step_index

    def load_state(self):
        created = False
        state = request.session.get(self.id)
        if not state:
            state = dict(step=self.start_index, data={})
            created = True

        self.state = state
        return created

    def save_state(self):
        request.session[self.id] = self.state

    def clear_needed_steps(self):
        if self.state is None:
            self.load_state()
        self.state['needed_steps'] = []
        self.save_state()

    def next(self):
        """Return next step of the wizard."""
        try:
            step_handlers = self.steps[self.current_step_index]
        except KeyError:
            raise StopIteration()
        else:
            try:
                return step_handlers['GET']
            except KeyError:
                raise MissingStepHandler(self.current_step_index, 'GET')

    def override_next_step(self):
        if self.allow_override:
            override_step = request.params.get(self.step_param)
            if override_step is not None:
                try:
                    step_index = int(override_step)
                except ValueError:
                    return
                else:
                    is_existing_step = step_index in self.steps
                    is_valid_step = step_index <= self.current_step_index
                    if is_existing_step and is_valid_step:
                        self.set_step_index(step_index)

    def redirect_to_step(self):
        query = '?{0}={1}'.format(self.step_param, self.current_step_index)
        return redirect(request.fullpath + query)

    def start_next_step(self):
        # in case the step param is missing, redirect to same url to include it
        if request.params.get('step') is None:
            return self.redirect_to_step()

        try:
            step = next(self)
        except StopIteration:
            return self.wizard_finished(self.state['data'])
        else:
            step_context = step['handler']()
            step_index = self.current_step_index
            return self.template_func(step['template'],
                                      step_index=self.current_step_index,
                                      step_count=self.step_count,
                                      step_param=self.step_param,
                                      step_name=self.steps[step_index]['name'],
                                      start_index=self.start_index,
                                      **step_context)

    def process_current_step(self):
        # could happen in case the saved state points to a higher step and in
        # the meantime a test condition made one of the steps to drop out and
        # a post request is sent to a step with an old higher index
        if self.current_step_index not in self.steps:
            return self.redirect_to_step()

        step_handlers = self.steps[self.current_step_index]
        try:
            step = step_handlers['POST']
        except KeyError:
            raise MissingStepHandler(self.current_step_index, 'POST')

        step_result = step['handler']()
        if not step_result.pop('successful', False):
            step_index = self.current_step_index
            return self.template_func(step['template'],
                                      step_index=self.current_step_index,
                                      step_count=self.step_count,
                                      step_param=self.step_param,
                                      step_name=self.steps[step_index]['name'],
                                      start_index=self.start_index,
                                      **step_result)

        self.state['data'][self.current_step_index] = step_result
        self.set_step_index(self.current_step_index + 1)
        self.save_state()
        return self.redirect_to_step()

    def wizard_finished(self, data):
        raise NotImplementedError()

    def request_step_index(self, name, index, next_free_index):
        if index is None:
            # check if a step is already registered by the same name
            for step_idx, step in self.steps.items():
                if step['name'] == name:
                    return step_idx
            # assign the next available index as no step was registered
            # previously with this name
            return next_free_index
        # index was explicitly specified by registerer, attempt to use it
        try:
            use_index = int(index)
            if use_index < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('Step index must be a positive integer.')
        else:
            return use_index

    def register_step(self, name, template, method=valid_methods, index=None,
                      test=None):
        def decorator(func):
            next_free_idx = max(self.steps.keys() + [self.start_index - 1]) + 1
            use_index = self.request_step_index(name, index, next_free_idx)

            if (use_index in self.steps and
                    self.steps[use_index]['name'] != name):
                # an auto-indexed handler probably have taken the place of this
                # manually indexed handler, switch their places
                self.steps[next_free_idx] = self.steps[use_index]
                del self.steps[use_index]

            methods = [method] if isinstance(method, basestring) else method
            for method_name in methods:
                if method_name not in self.valid_methods:
                    msg = '{0} is not an acceptable HTTP method.'.format(
                        method_name
                    )
                    raise ValueError(msg)
                self.steps.setdefault(use_index, dict(name=name))

                if not callable(test):
                    raise TypeError('`test` parameter must be a callable.')
                self.steps[use_index]['test'] = test

                self.steps[use_index][method_name] = {'handler': func,
                                                      'template': template}
            return func
        return decorator

    def remove_gaps(self):
        """Inplace removal of eventual gaps between registered step indexes."""
        original = [None] * (max(self.steps.keys() or [self.start_index]) + 1)
        for idx, step in self.steps.items():
            original[idx] = step

        gapless = [step for step in original if step is not None]
        self.steps = dict((self.start_index + idx, step)
                          for idx, step in enumerate(gapless))

    def get_needed_steps(self):
        return [idx for idx, step in self.steps.items()
                if step.get('test', lambda: True)()]

    def skip_needless_steps(self, needed_steps):
        self.steps = dict((idx, step) for idx, step in self.steps.items()
                          if idx in needed_steps)

    @classmethod
    def create_wizard(cls, name, attrs):
        instance = cls(name)
        # make sure attributes that were assigned after the wizard instance was
        # created will be passed on to new instances as well
        for name, value in attrs.items():
            setattr(instance, name, value)

        return instance
