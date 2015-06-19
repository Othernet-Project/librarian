"""
flat.py: Flat pages

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request

from .template import template


class FlatPage(object):
    """Renders flatpage object on first access using the request locale, and
    stores the rendered version in a dict associating it with the locale code
    in use, so on subsequent accesses a re-rendering of the page won't be
    needed."""
    def __init__(self, name, path):
        self.__name__ = name
        self.path = path
        self.versions = dict()

    def __call__(self):
        locale = getattr(request, 'locale', '_')
        try:
            rendered = self.versions[locale]
        except KeyError:
            rendered = template(self.path)
        return rendered


class FlatPageRegistry(object):
    """Initializes flat_page objects on first access, and uses existing ones on
    subsequent accesses."""
    def __init__(self, root=''):
        self.root = root
        self.pages = dict()

    def get_or_create(self, name):
        try:
            flat_page = self.pages[name]
        except KeyError:
            full_path = os.path.join(self.root, name)
            flat_page = self.pages[name] = FlatPage(name, full_path)

        return flat_page

    def __getattr__(self, name):
        return self.get_or_create(name)

    def __getitem__(self, name):
        return self.get_or_create(name)


def flat_plugin(app):
    app.exts.flat_pages = FlatPageRegistry(app.config['flat.root'])
