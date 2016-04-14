"""
setup.py: Basic setup wizard steps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from streamline import RouteBase, TemplateRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..helpers.ondd import has_tuner
from ..utils.route_mixins import RedirectRouteMixin


def iter_lines(lines):
    while lines:
        yield lines.pop()


class Diag(TemplateRoute):
    path = '/diag/'
    template_func = template
    template_name = 'diag/diag'

    def get(self):
        if exts.setup_wizard.is_completed:
            self.redirect('/')
        logpath = self.config['logging.syslog']
        with open(logpath, 'rt') as log:
            logs = iter_lines(list(log)[-100:])
        return dict(logs=logs, has_tuner=has_tuner())


class Enter(RouteBase):
    path = '/setup/'

    def get(self):
        return exts.setup_wizard()


class Exit(RedirectRouteMixin, RouteBase):
    path = '/setup/exit/'

    def get(self):
        exts.setup_wizard.exit()
        self.perform_redirect()
