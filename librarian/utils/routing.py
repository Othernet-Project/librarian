"""
routing.py: Routing helpers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

def add_routes(app, routes):
    """ Add routes to app """

    for route in routes:
        name, cb, method, path, kw = route
        app.route(path, method, cb, name=name, **kw)
