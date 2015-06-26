"""
menuitem.py: main menu plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import importlib

import bottle

from bottle_utils import html
from bottle_utils.i18n import i18n_url


MENU_ITEMS = []
MENU_GROUPS = {}


class MenuItem(object):
    label = ''
    group = None
    icon_class = ''
    alt_icon_class = ''
    route = None
    default_classes = ('navicon',)
    name = None

    def is_alt_icon_visible(self):
        return False

    def is_visible(self):
        return True

    def get_path(self):
        return i18n_url(self.route)

    def render(self):
        if not self.is_visible():
            return ''
        if self.is_alt_icon_visible():
            icon_class = self.alt_icon_class
        else:
            icon_class = self.icon_class
        if icon_class:
            icon = html.SPAN(_class="icon")
        else:
            icon = ''

        item_class = ' '.join(
            tuple(self.default_classes) + (icon_class,)).strip()
        return html.link_other(
            ' '.join([icon + html.SPAN(self.label, _class="label")]),
            self.get_path(), bottle.request.original_path,
            lambda s, _class: html.SPAN(s, _class='active ' + item_class),
            _class=item_class)

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()


def find_menu_cls(mod):
    for member in dir(mod):
        member = getattr(mod, member)
        if issubclass(member, MenuItem) and member is not MenuItem:
            return member
    raise ValueError('Could not find MenuItem subclass in {}'.format(
        mod.__name__))


def install_menuitems(app):
    for (name, group) in app.config.items():
        if not name.startswith('menu.'):
            continue
        group_name = name.replace('menu.', '')

        for mod_path in group:
            name = mod_path.rsplit('.', 1)[-1]
            try:
                # Attempt global import
                mod = importlib.import_module(mod_path)
            except ImportError:
                # Attempt local import
                rel_path = 'librarian.menu.{0}'.format(mod_path)
                mod = importlib.import_module(rel_path)

            menu_cls = find_menu_cls(mod)
            menu_cls.name = name
            MENU_ITEMS.append(menu_cls)
            MENU_GROUPS.setdefault(group_name, [])
            MENU_GROUPS[group_name].append(menu_cls)

    bottle.BaseTemplate.defaults.update({'menu_group': menu_group,
                                         'menu_item': menu_item})


def menu_group(group):
    """Return list of menu items that belong to the specified `group`"""
    for item in MENU_GROUPS[group]:
        yield item()


def menu_item(name, group=None):
    """Return a single menu item that matches the given name. It looks through
    either the whole list of menu items, or if `group` is specified, only on
    the subset belonging to that group."""
    items = menu_group(group) if group else MENU_ITEMS
    for item in items:
        if item.name == name:
            return item()
