import functools

from bottle import request

from ...exts import ext_container as exts
from .sessions import SessionExpired, SessionInvalid, Session


# Set up a hook, so handlers that raise cannot escape session-saving
def save_session():
    if hasattr(request, 'session'):
        if request.session.modified:
            request.session.save()

        cookie_name = exts.config['session.cookie_name']
        secret = exts.config['session.secret']
        request.session.set_cookie(cookie_name, secret)


def session_plugin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        cookie_name = exts.config['session.cookie_name']
        secret = exts.config['session.secret']
        session_id = request.get_cookie(cookie_name, secret=secret)
        try:
            request.session = Session.fetch(session_id)
        except (SessionExpired, SessionInvalid):
            request.session = Session.create()
        return fn(*args, **kwargs)
    return wrapper
session_plugin.name = 'session_plugin'
