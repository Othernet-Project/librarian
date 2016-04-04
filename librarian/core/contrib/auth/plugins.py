import functools

from bottle import request

from .users import User


EXPORTS = {
    'user_plugin': {
        'depends_on': [
            'librarian_core.contrib.sessions.plugins.session_plugin'
        ]
    }
}


def user_plugin(supervisor):
    # Set up a hook, so handlers that raise cannot escape session-saving
    @supervisor.app.hook('after_request')
    def store_user_in_session():
        if hasattr(request, 'session') and hasattr(request, 'user'):
            request.user.options.collect()
            request.session['user'] = request.user.to_json()

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            request.no_auth = supervisor.config['args'].no_auth
            user_data = request.session.get('user', '{}')
            request.user = User.from_json(user_data)
            request.user.options.process()
            return callback(*args, **kwargs)

        return wrapper
    plugin.name = 'user'
    return plugin
