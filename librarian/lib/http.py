"""
.. module:: bottle_utils.http
   :synopsis: HTTP decorators

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import functools

from bottle import response


def no_cache(func):
    """
    Disable caching on a handler. The decorated handler will have
    ``Cache-Control`` header set to ``private, no-cache``.

    This is useful for responses that contain data that cannot be reused.

    Simply deocrate a handler with it::

        @app.get('/foo')
        @no_cache
        def not_cached():
            return 'sensitive data'
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        response.headers[b'Cache-Control'] = b'private, no-cache'
        return resp
    return wrapper

