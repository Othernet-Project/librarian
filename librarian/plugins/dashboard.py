"""
dashboard.py: dashboard plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import bottle


class DashboardPlugin(object):
    heading = None
    name = None
    javascript = None
    template_lookup_base = os.path.dirname(__file__)

    def get_name(self):
        """ Return section name """
        return self.name

    def get_heading(self):
        """ Return dashboard section heading """
        return self.heading

    def get_javascript(self):
        return self.javascript or ''

    def get_context(self):
        """ Return variables for the dashboard section template """
        return {}

    def get_template(self):
        """ Return template name """
        return self.name

    def get_template_lookup_base(self):
        return self.template_lookup_base

    def get_template_dir(self):
        return os.path.join(self.get_template_lookup_base(),
                            self.get_name(),
                            'views')

    def render_script(self):
        if not self.javascript:
            return ''
        return ('<script src="/static/plugins/%s/dashboard.js">'
                '</script>') % self.get_name()

    def render(self):
        """ Render dashboard section """
        context = {
            'name': self.get_name(),
            'heading': self.get_heading(),
        }
        context.update(self.get_context())
        template_dirs = [self.get_template_dir()] + bottle.TEMPLATE_PATH
        main = bottle.template(self.get_template(),
                               template_lookup=template_dirs,
                               **context)
        javascript = self.get_javascript()
        return main + javascript

