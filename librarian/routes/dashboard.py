"""
dashboard.py: routes related to dashboard and configuration management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from streamline import TemplateRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..decorators.auth import login_required


class Dashboard(TemplateRoute):
    name = 'dashboard:main'
    path = '/dashboard/'
    template_func = template
    template_name = 'dashboard/dashboard'

    @login_required()
    def get(self):
        return dict(plugins=exts.dashboard.plugins)
