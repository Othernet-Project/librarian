"""
menu.py: main menu plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils import html
from bottle_utils.i18n import i18n_url


class MenuItem(object):
    """ Represents a menu item """

    #: Menu group
    group = None

    #: Menu item label (use lazy object to make it dynamic)
    label = ''

    #: Named route which menu item targets
    route = None

    #: Menu item identifier
    name = None

    #: Whether icon is a bitmap (set to ``False`` to use icon classes instead)
    icon_is_bitmap = False

    #: Menu icon class
    icon_class = ''

    #: Alternative state menu item class (see ``is_alt_icon_visible()``)
    alt_icon_class = ''

    #: Path to the icon bitmap (path is under ``sys:static`` route)
    icon_bitmap_path = None

    #: Path to alternative bitmap (path is under ``sys:static``)
    alt_icon_bitmap_path = None

    def is_alt_icon_visible(self):
        """ Whether alternative icon is selected

        Overload this method in subclass to customize the condition under which
        the alternative icon is selected.
        """
        return False

    def is_visible(self):
        """ Whether icon is rendered in the UI

        Overload this method in subclass to customize the condition under which
        the visibility is enabled or disabled.
        """
        return True

    def get_path(self):
        """ Return the full target path based on the route

        If you need to conditionally construct the path, or pass it additional
        parameters, overload this method in your subclass.
        """
        return i18n_url(self.route)

    @property
    def active_icon_class(self):
        """ Active class for the icon based on ``is_alt_icon_visible`` """
        if self.is_alt_icon_visible():
            return self.alt_icon_class
        return self.icon_class

    @property
    def active_icon_bitmap_path(self):
        """ Active path for the icon based on ``is_alt_icon_visible`` """
        if self.is_alt_icon_visible():
            return self.alt_icon_bitmap_path
        return self.icon_bitmap_path

    def __str__(self):
        return '<MenuItem "{}" for {}>'.format(self.name, self.route)
