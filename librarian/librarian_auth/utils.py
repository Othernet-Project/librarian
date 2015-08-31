"""
http.py: HTTP Utility functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import random
import string
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


def generate_secret_key(length=50):
    charset = [string.ascii_letters, string.digits, string.punctuation]
    chars = (''.join(charset).replace('\'', '')
                             .replace('"', '')
                             .replace('\\', ''))
    return ''.join([random.choice(chars) for i in range(length)])


def from_csv(raw_value):
    return [val.strip() for val in (raw_value or '').split(',') if val]


def to_csv(values):
    return ','.join(values)


def row_to_dict(row):
    return dict((key, row[key]) for key in row.keys())
