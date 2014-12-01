"""
favorites.py: routes related to favorites

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, view, abort, redirect, default_app

from ..lib.favorites import favorite_content, mark_favorite
from ..lib.i18n import i18n_path, lazy_gettext as _

__all__ = ('app', 'list_favorites', 'add_favorite',)


app = default_app()


@view('favorites.tpl')
def list_favorites():
    """ List of favorite content """
    return {'metadata': favorite_content()}


def add_favorite():
    """ Add/remove content to favorites list """
    md5 = request.forms.get('md5')
    try:
        val = int(request.forms.get('fav', '1'))
    except (TypeError, ValueError):
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))
    if (not md5) or (not mark_favorite(md5, val)):
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))
    redirect(i18n_path('/favorites/'))

