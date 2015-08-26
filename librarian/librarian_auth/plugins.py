import functools

from bottle import request, hook

from .sessions import SessionExpired, SessionInvalid, Session
from .users import User


EXPORTS = {
    'session_plugin': {'depends_on': ['librarian.librarian_sqlite.plugins.plugin']},  # TODO: remove librarian. prefix
    'user_plugin': {'depends_on': ['librarian.librarian_auth.plugins.session_plugin']}  # TODO: remove librarian. prefix
}


def session_plugin(supervisor):
    cookie_name = supervisor.config['session.cookie_name']
    secret = supervisor.config['session.secret']

    # Set up a hook, so handlers that raise cannot escape session-saving
    @hook('after_request')
    def save_session():
        if hasattr(request, 'session'):
            if request.session.modified:
                request.session.save()

            request.session.set_cookie(cookie_name, secret)

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            session_id = request.get_cookie(cookie_name, secret=secret)
            try:
                request.session = Session.fetch(session_id)
            except (SessionExpired, SessionInvalid):
                request.session = Session.create()
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'session'
    return plugin


def user_plugin(supervisor):
    # Set up a hook, so handlers that raise cannot escape session-saving
    @hook('after_request')
    def process_options():
        if hasattr(request, 'session') and hasattr(request, 'user'):
            request.user.options.apply()
            request.session['user'] = request.user.to_json()

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            request.no_auth = supervisor.config['args'].no_auth
            user_data = request.session.get('user', '{}')
            request.user = User.from_json(user_data)
            return callback(*args, **kwargs)

        return wrapper
    plugin.name = 'user'
    return plugin
