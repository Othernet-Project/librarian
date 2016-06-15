import functools

from bottle import request, abort

from ..utils.lock import is_locked


def lock_plugin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        unlocked = request.route.config.get('unlocked', False)
        if not unlocked and is_locked():
            abort(503, 'Librarian is locked')
        return fn(*args, **kwargs)
    return wrapper
lock_plugin.name = 'lock_plugin'
