"""
routes.py: common utility routes

Copyright 2015, Outernet Inc.

Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from streamline import XHRPartialRoute

from ..core.contrib.templates.renderer import template
from ..helpers import lang  # NOQA


class List(XHRPartialRoute):
    name = 'ui:lang_list'
    path = '/languages/'
    template_func = template
    template_name = 'ui/lang_list'
    partial_template_name = 'ui/_lang_list'
