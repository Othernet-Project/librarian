"""
flats.py: routes to flat pages

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


def routes(app):
    return (
        ('flat:about', app.exts.flat_pages.about, 'GET', '/about/', {}),
        ('flat:faq', app.exts.flat_pages['faq'], 'GET', '/faq/', {}),
    )
