"""
routes.py: common utility routes

Copyright 2015, Outernet Inc.

Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.ajax import roca_view

from librarian_core.contrib.templates.renderer import template


EXPORTS = {
        'routes': {'required_by':
                   ['librarian_core.contrib.system.routes.routes']}
}


@roca_view('ui/lang_list', 'ui/_lang_list', template_func=template)
def lang_list():
    return dict()


def routes(config):
    return (
        ('ui:lang_list', lang_list, 'GET', '/languages/', {}),
    )
