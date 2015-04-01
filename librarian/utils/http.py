"""
http.py: HTTP Utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import urlparse

from bottle import request, response


def http_redirect(path, code=303):
    """Redirect to the specified path. Replacement for bottle's builtin
    redirect function, because it loses newly set cookies.

    :param path:  Redirect to specified path
    """
    response.set_header('Location', urlparse.urljoin(request.url, path))
    response.status = code
    response.body = ""
    return response
