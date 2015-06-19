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
        key = '{0}_{1}'.format(self.__name__, locale)
        if request.app.exts.is_installed('cache'):
            # use cache if available
            source = request.app.exts.cache
        else:
            # fallback to in-memory dict
            source = self.versions

        rendered = source.get(key)
        if rendered is None:
            rendered = template(self.path)
            source.set(key, rendered)

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
