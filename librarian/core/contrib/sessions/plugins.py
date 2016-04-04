import functools

from bottle import request

from .sessions import SessionExpired, SessionInvalid, Session


EXPORTS = {
    'session_plugin': {
        'depends_on': ['librarian_core.contrib.databases.plugins.plugin']
    },
}


def session_plugin(supervisor):
    # Set up a hook, so handlers that raise cannot escape session-saving
    @supervisor.app.hook('after_request')
    def save_session():
        if hasattr(request, 'session'):
            if request.session.modified:
                request.session.save()

            cookie_name = supervisor.config['session.cookie_name']
            secret = supervisor.config['session.secret']
            request.session.set_cookie(cookie_name, secret)

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            cookie_name = supervisor.config['session.cookie_name']
            secret = supervisor.config['session.secret']
            session_id = request.get_cookie(cookie_name, secret=secret)
            try:
                request.session = Session.fetch(session_id)
            except (SessionExpired, SessionInvalid):
                request.session = Session.create()
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'session'
    return plugin
