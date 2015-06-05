"""
menuitem.py: main menu plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys
import functools

import bottle

from bottle_utils import html
from bottle_utils.i18n import i18n_url


MENU_ITEMS = []


class MenuItem(object):
    label = ''
    group = None
    icon = None
    alt_icon = None
    route = None
    static_route = 'menuitems:{0}:static'
    static_path = '/m/{0}/<path:path>'
    default_classes = ('navicon',)

    def __init__(self, app):
        mod_file = sys.modules[self.__class__.__module__].__file__
        pkg_path = os.path.dirname(os.path.abspath(mod_file))
        self.name = os.path.basename(pkg_path)
        self._install_static_handler(app, pkg_path, self.name)

    def _install_static_handler(self, app, pkg_path, name):
        static_root = os.path.join(pkg_path, 'static')
        if not os.path.isdir(static_root):
            return

        route_static = lambda path: bottle.static_file(path, static_root)
        route_static.__name__ = '_route_{0}_static'.format(name)
        app.route(self.static_path.format(name),
                  'GET',
                  route_static,
                  name=self.static_route.format(name),
                  no_i18n=True,
                  skip=app.APP_ONLY_PLUGINS)

    def is_alt_icon_visible(self):
        return False

    def is_visible(self):
        return True

    def render(self):
        IMAGE = functools.partial(html.tag, 'img')
        static_route = self.static_route.format(self.name)
        if self.is_alt_icon_visible():
            icon_path = self.alt_icon
        else:
            icon_path = self.icon

        icon = IMAGE(src=i18n_url(static_route, path=icon_path))
        item_class = ' '.join(tuple(self.default_classes) + (self.name,))
        return html.link_other(icon + self.label,
                               i18n_url(self.route),
                               bottle.request.original_path,
                               html.SPAN,
                               _class=item_class)

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()


def install_menuitems(app):
    for item_pkg_path in app.config.get('menu.items', []):
        mod_path = '{0}.menuitem'.format(item_pkg_path)
        try:
            __import__(mod_path)  # attempt import from pythonpath
        except ImportError:
            rel_path = 'librarian.menu.{0}'.format(mod_path)
            __import__(rel_path)  # attempt local import

    for menu_item_cls in MenuItem.__subclasses__():
        MENU_ITEMS.append(menu_item_cls(app))

    bottle.BaseTemplate.defaults.update({'menu_group': menu_group,
                                         'menu_item': menu_item})


def menu_group(group):
    for item in MENU_ITEMS:
        if item.group == group:
            yield item


def menu_item(name, group=None):
    items = menu_group(group) if group else MENU_ITEMS
    for item in items:
        if item.name == name:
            return item
