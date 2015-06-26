
"""
template.py: Mako template renderer, based on bottle's class but includes
             optimizations that otherwise cannot be applied.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools

import bottle

from bottle_utils import html
from bottle_utils.common import to_unicode
from mako.template import Template
from mako.lookup import TemplateLookup

from .template_helpers import template_helper
from .lang import LANGS, UI_LANGS, SELECT_LANGS


def configure_template(app):
    bottle.TEMPLATE_PATH.insert(0, app.in_pkg('views'))
    bottle.BaseTemplate.defaults.update({
        'app_version': app.version,
        'request': bottle.request,
        'h': html,
        'th': template_helper,
        'LANGS': LANGS,
        'UI_LANGS': UI_LANGS,
        'SELECT_LANGS': SELECT_LANGS,
        'u': to_unicode,
        'url': app.get_url,
        'REDIRECT_DELAY': app.config.get('librarian.redirect_delay', 10)
    })


class MakoTemplate(bottle.BaseTemplate):

    def prepare(self, **options):
        is_debug = bool(bottle.DEBUG)
        module_directory = bottle.request.app.config['mako.module_directory']
        options.update({'input_encoding': self.encoding})
        options.setdefault('format_exceptions', is_debug)
        lookup = TemplateLookup(directories=self.lookup,
                                filesystem_checks=is_debug,
                                module_directory=module_directory,
                                **options)
        if self.source:
            self.tpl = Template(self.source, lookup=lookup, **options)
        else:
            self.tpl = Template(uri=self.name,
                                filename=self.filename,
                                lookup=lookup, **options)

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)
        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults)


template = functools.partial(bottle.template, template_adapter=MakoTemplate)
view = functools.partial(bottle.view, template_adapter=MakoTemplate)
