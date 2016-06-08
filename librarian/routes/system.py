"""
routes.py: System routes such as static files and error handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from bottle import request
from bottle_utils.i18n import i18n_url
from streamline import RouteBase

from ..core.contrib.i18n.utils import is_i18n_enabled
from ..core.contrib.templates.renderer import view


class RootRoute(RouteBase):
    path = '/'

    def get(self):
        route = self.config['app.default_route']
        route_args = self.config.get('app.default_route_args', [])
        route_args = dict(arg.split(':') for arg in route_args)
        if hasattr(self.request, 'default_route'):
            route = self.request.default_route

        if is_i18n_enabled():
            url = i18n_url(route, **route_args)
        else:
            url = self.request.app.get_url(route, *route_args)

        self.redirect(url)


class All404Route(RouteBase):
    path = '/<path:path>'
    depends_on = 'sys:static'

    def get(self, path):
        self.abort(404)

    def post(self, path):
        self.abort(404)


@view('errors/403')
def error_403(exc):
    return dict()


@view('errors/404')
def error_404(exc):
    return dict(redirect_url='/')


@view('errors/500')
def error_500(exc):
    traceback = exc.traceback or exc.body
    logging.error("Unhandled error '%s' at %s %s:\n\n%s",
                  exc.exception,
                  request.method.upper(),
                  request.path,
                  traceback)
    return dict(trace=traceback)


@view('errors/503')
def error_503(exc):
    return dict()