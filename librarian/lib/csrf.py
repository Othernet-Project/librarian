"""
.. module:: bottle_utils.csrf
   :synopsis: CSRF-protection decorators

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import os
import hashlib
import functools

from bottle import request, response, abort

from .html import HIDDEN
from .common import to_unicode

ROOT = '/'
CSRF_TOKEN = '_csrf_token'
EXPIRES = 600  # seconds
ENCODING = 'latin1'


def get_conf():
    """
    Return parsed configruation options. This function obtains

    This function raises ``KeyError`` if configuration misses

    :raises: KeyError
    :returns: tuple of secret, token name, path, and cookie timeout
    """
    conf = request.app.config
    csrf_secret = conf['csrf.secret']
    csrf_token_name = str(conf.get('csrf.token_name', CSRF_TOKEN))
    csrf_path = conf.get('csrf.path', ROOT).encode(ENCODING)
    try:
        cookie_expires = int(conf.get('csrf.expires', EXPIRES))
    except ValueError:
        cookie_expires = EXPIRES
    return csrf_secret, csrf_token_name, csrf_path, cookie_expires


def generate_csrf_token():
    """
    Generate and set new CSRF token in cookie. The generated token is set to
    ``request.csrf_token`` attribute for easier access by other functions.

    It is generally not necessary to use this function directly.

    .. warning::

       This function uses ``os.urandom()`` call to obtain 8 random bytes when
       generating the token. It is possible to deplete the randomness pool and
       make the random token predictable.
    """
    secret, token_name, path, expires = get_conf()
    sha256 = hashlib.sha256()
    sha256.update(os.urandom(8))
    token = sha256.hexdigest().encode(ENCODING)
    response.set_cookie(token_name, token, path=path,
                        secret=secret, max_age=expires)
    request.csrf_token = token.decode(ENCODING)


def csrf_token(func):
    """
    Create and set CSRF token in preparation for subsequent POST request. This
    decorator is used to set the token. It also sets the ``'Cache-Control'``
    header in order to prevent caching of the page on which the token appears.

    When an existing token cookie is found, it is reused. The existing token is
    reset so that the expiration time is extended each time it is reused.

    The POST handler must use the :py:func:`~bottle_utils.csrf.csrf_protect`
    decotrator for the token to be used in any way.

    The token is available in the ``bottle.request`` object as ``csrf_token``
    attribute::

        @app.get('/')
        @bottle.view('myform')
        @csrf_token
        def put_token_in_form():
            return dict(token=request.csrf_token)

    In a view, you can render this token as a hidden field inside the form. The
    hidden field must have a name ``_csrf_token``::

        <form method="POST">
            <input type="hidden" name="_csrf_token" value="{{ csrf_token }}">
            ....
        </form>
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        secret, token_name, path, expires = get_conf()
        token = request.get_cookie(token_name, secret=secret)
        if token:
            # We will reuse existing tokens
            response.set_cookie(token_name, token, path=path,
                                secret=secret, max_age=expires)
            request.csrf_token = token.decode('utf8')
        else:
            generate_csrf_token()
        # Pages with CSRF tokens should not be cached
        response.headers[str('Cache-Control')] = 'private no-cache'
        return func(*args, **kwargs)
    return wrapper


def csrf_protect(func):
    """
    Perform CSRF protection checks. Performs checks to determine if submitted
    form data matches the token in the cookie. It is assumed that the GET
    request handler successfully set the token for the request and that the
    form was instrumented with a CSRF token field. Use the
    :py:func:`~bottle_utils.csrf.csrf_token` decorator to do this.

    If the handler function returns (i.e., it is not interrupted with
    ``bottle.abort()``, ``bottle.redirect()``, and similar functions that throw
    an exception, a new token is set and response is returned to the requester.
    It is therefore recommended to perform a reidrect on successful POST.

    Generally, the handler does not need to do anything
    CSRF-protection-specific. All it needs is the decorator::

        @app.post('/')
        @bottle.view('myform')
        @csrf_protect
        def protected_post_handler():
            if successful:
                redirect('/someplace')
            return dict(errors="There were some errors")

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        secret, token_name, path, expires = get_conf()
        token = request.get_cookie(token_name, secret=secret)
        if not token:
            abort(403, 'The form you submitted is invalid or has expired')
        form_token = request.forms.get(token_name)
        if to_unicode(form_token) != to_unicode(token):
            response.delete_cookie(token_name, path=path, secret=secret,
                                   max_age=expires)
            abort(403, 'The form you submitted is invalid or has expired')
        generate_csrf_token()
        return func(*args, **kwargs)
    return wrapper


def csrf_tag():
    """
    Generte HTML for hidden form field. This is a convenience function to
    generate a simple hidden input field. It does not accept any arguments
    since it uses the ``bottle.request`` object to obtain the token.

    If the handler in which this function is invoked is not decorated with
    :py:func:`~bottle_utils.csrf.csrf_token`, an ``AttributeError`` will be
    raised.

    :returns:   HTML markup for hidden CSRF token field
    """
    _, token_name, _, _ = get_conf()
    token = request.csrf_token
    try:
        token_name = token_name.decode('utf8')
    except AttributeError:
        pass
    return HIDDEN(token_name, token)

