# -*- coding: utf-8 -*-

"""
Install routes specified in configuration

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


def install_routes(app):
    for route_path in app.config['librarian.routes']:
        splitted = route_path.split('.')
        func_name = splitted[-1]
        mod_path = '.'.join(splitted[:-1])
        route_mod = __import__(mod_path, fromlist=[func_name])
        route_conf_getter = getattr(route_mod, func_name)
        for route in route_conf_getter(app):
            name, cb, method, path, kw = route
            app.route(path, method, cb, name=name, **kw)
