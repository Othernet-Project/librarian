import functools

from bottle import request

from ...exports import depends_on
from .users import User


# Set up a hook, so handlers that raise cannot escape session-saving
def store_user_in_session():
    if hasattr(request, 'session') and hasattr(request, 'user'):
        request.user.options.collect()
        request.session['user'] = request.user.to_json()


@depends_on('session_plugin')
def user_plugin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        request.no_auth = request.app.config['args'].no_auth
        user_data = request.session.get('user', '{}')
        request.user = User.from_json(user_data)
        request.user.options.process()
        return fn(*args, **kwargs)
    return wrapper
user_plugin.name = 'user_plugin'
