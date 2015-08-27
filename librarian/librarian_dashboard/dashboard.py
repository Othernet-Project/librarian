"""
dashboard.py: dashboard plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import os

from ..utils.template import template


class DashboardPlugin(object):
    """ Base class for dashboard plugins

    This class is used in conjunction with ``_dashboard_section.tpl`` template
    to display plugin controls on the dashboard.

    The object returns the name of the dashboard section (should be
    i18n-enabled), and renders a template for the section. The rendered HTML
    may also include a ``<script>`` tag for linking JavaScript files if such
    files.

    Subclass can overload any number of methods and properties, but the usual
    candidate is the ``get_context()`` which provides extra context to the
    template being rendered. The context should be a dict, and they are passed
    as exra keyword arguments to ``bottle.template()`` call.

    The ``name`` propery defines the name of the section. This name is assigned
    as ``class`` and ``id`` attributes on the container element (with ``dash-``
    prefix when used in ``class`` attribute). You can return different names
    dynamically by overloading the ``get_name()`` method.

    The ``name`` property also determines the name of the template directory
    that will be looked up. If you wish to use a different name or different
    template directory, you can overload the ``get_template_dir()`` method.
    """

    heading = None
    name = None
    javascript = []
    template_lookup_base = os.path.dirname(__file__)
    classes = ['collapsible', 'collapsed']
    plugin_error_template = 'plugin_error.tpl'

    def get_name(self):
        """ Return section name """
        return self.name

    def get_heading(self):
        """ Return dashboard section heading """
        return self.heading

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

    def get_classes(self):
        return self.classes

    def get_formatted_classes(self):
        return ' '.join([('dash-%s' % c) for c in self.get_classes()])

    def get_javascript(self):
        return self.javascript

    def render(self):
        """ Render dashboard section """
        name = self.get_name()
        context = {
            'plugin': self,
            'name': name,
            'heading': self.get_heading(),
            'classes': self.get_formatted_classes(),
        }
        try:
            context.update(self.get_context())
            return template(self.get_template(), **context)
        except Exception:
            logging.exception("Plugin rendering failed: {0}".format(name))
            return template(self.plugin_error_template, **context)

    def render_javascript(self):
        html = ''
        for js in self.get_javascript():
            html += '<script src="/s/%s/%s"></script>' % (self.name, js)
        return html

    def __str__(self):
        return "<DashboardPlugin '%s'>" % self.name
