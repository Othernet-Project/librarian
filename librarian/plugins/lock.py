import functools

from bottle import request, abort

from .lock import is_locked


def plugin(supervisor):
    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            unlocked = request.route.config.get('unlocked', False)
            if not unlocked and is_locked():
                abort(503, 'Librarian is locked')
            return callback(*args, **kwargs)
        return wrapper
    return decorator
