"""
menuitem.py: main menu plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys

import bottle

from bottle_utils import html
from bottle_utils.i18n import i18n_url


MENU_ITEMS = []


class MenuItem(object):
    label = ''
    group = None
    icon_class = None
    alt_icon_class = None
    route = None
    default_classes = ('navicon',)

    def __init__(self, app):
        mod_file = sys.modules[self.__class__.__module__].__file__
        pkg_path = os.path.dirname(os.path.abspath(mod_file))
        self.name = os.path.basename(pkg_path)

    def is_alt_icon_visible(self):
        return False

    def is_visible(self):
        return True

    def render(self):
        icon = html.SPAN(_class="icon")
        if self.is_alt_icon_visible():
            icon_class = self.alt_icon_class
        else:
            icon_class = self.icon_class

        item_class = ' '.join(tuple(self.default_classes) + (icon_class,))
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
    for mod_path in app.config.get('menu.items', []):
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
    """Return list of menu items that belong to the specified `group`"""
    for item in MENU_ITEMS:
        if item.group == group:
            yield item


def menu_item(name, group=None):
    """Return a single menu item that matches the given name. It looks through
    either the whole list of menu items, or if `group` is specified, only on
    the subset belonging to that group."""
    items = menu_group(group) if group else MENU_ITEMS
    for item in items:
        if item.name == name:
            return item
