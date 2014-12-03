"""
.. module:: bottle_utils.common
   :synopsis: Common utility functions

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import sys
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from bottle import request, html_escape

__all__ = ('PY3', 'PY2', 'unicode', 'basestring', 'to_unicode', 'to_bytes',
           'attr_escape', 'html_escape', 'full_url', 'urlquote')

ESCAPE_MAPPING = (
    ('&', '&amp;'),
    ('"', '&quot;'),
    ('\n', '&#10;'),
    ('\r', '&#13;'),
    ('\t', '&#9;'),
)

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3


if PY3:
    basestring = str
    unicode = str
if PY2:
    unicode = unicode
    basestring = basestring


def to_unicode(v, encoding='utf8'):
    """
    Convert a value to Unicode string (or just string in Py3). This function
    can be used to ensure string is a unicode string. This may be useful when
    input can be of different types (but meant to be used when input can be
    either bytestring or Unicode string), and desired output is always Unicode
    string.

    :param v:           value
    :param encoding:    character set for decoding bytestrings
    :returns:           value as Unicode string
    """
    if isinstance(v, unicode):
        return v
    try:
        return v.decode(encoding)
    except (AttributeError, UnicodeEncodeError):
        return unicode(v)


def to_bytes(v, encoding='utf8'):
    """
    Convert a value to bytestring (or just string in Py2). This function is
    useful when desired output is always a bytestring, and input can be any
    type (although it is intended to be used with strings and bytestrings).

    :param v:           value
    :param encoding:    character set for encoding strings
    :returns:           value as bytestring
    """
    if isinstance(v, bytes):
        return v
    try:
        return v.encode(encoding, errors='ignore')
    except AttributeError:
        return unicode(v).encode(encoding)


def attr_escape(attr):
    """
    Escape HTML attribute values. This function escapes certain characters that
    are undesirable in HTML attributes. Functions that construct attribute
    values using user-supplied data should escape the values using this
    function.

    :param attr:    attribute value
    :returns:       escaped attribute value
    """
    for s, r in ESCAPE_MAPPING:
        attr = attr.replace(s, r)
    return attr


def full_url(path='/'):
    """
    Convert a specified path to full URL based on request data. This function
    uses the current request context information about the request URL to
    construct a full URL using specified path. In particular it uses
    ``bottle.request.urlparts`` to obtain information about scheme, hostname,
    and port (if any).

    Because it uses the request context, it cannot be called outside a request.

    :param path:    absolute path
    :returns:       full URL including scheme and hostname
    """
    parts = request.urlparts
    url = parts.scheme + '://' + parts.hostname
    if parts.port:
        url += ':' + str(parts.port)
    return url + path


def urlquote(s):
    """
    Quote (URL-encode) a string with Unicode support. This is a simple wrapper
    for ``urllib.quote`` (or ``urllib.parse.quote``) that converts the input to
    UTF-8-encoded bytestring before quoting.

    :param s:   URL component to escape
    :returns:   encoded URL component
    """
    s = to_bytes(s)
    return quote(s)
