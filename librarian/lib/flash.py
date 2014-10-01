"""
.. module:: bottle_utils.flash
   :synopsis: Cookie-based flash messages

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import sys
import functools

from bottle import request, response

from .lazy import lazy

from .common import PY2


MESSAGE_KEY = str('_flash')
ROOT = b'/'

# This is not to keep cookie content secret, it's to allow UTF8 cookies
SECRET = 'flash'


@lazy
def get_message():
    """
    Return currently set message and delete the cookie. This function is lazily
    evaluated so it's side effect of removing the cookie will only become
    effective when you actually use the message it returns.

    :returns: message
    """
    response.delete_cookie(MESSAGE_KEY, path=ROOT, secret=SECRET)
    return request._message


def set_message(msg):
    """
    Sets a message and makes it available via ``request`` object. This function
    sets the message cookie and assigns the message to the
    ``bottle.request._message`` attribute.

    In Py2, the message is UTF-8 encoded.

    :param msg: message string
    """
    if PY2:
        msg = msg.encode('utf8')
    response.set_cookie(MESSAGE_KEY, msg, path=ROOT, secret=SECRET)
    request._message = msg


def message_plugin(func):
    """
    Manages flash messages. This is a Bottle plugin that adds attributes to
    ``bottle.request`` and ``bottle.response`` objects for setting and
    consuming the flash messages.

    See `How it works`_.

    Example::

        bottle.install(message_plugin)

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cookie = request.get_cookie(MESSAGE_KEY, str(), secret=SECRET)
        if PY2:
            request._message = cookie.decode('utf8')
        else:
            request._message = cookie
        request.message = get_message()
        response.flash = set_message
        return func(*args, **kwargs)
    return wrapper

