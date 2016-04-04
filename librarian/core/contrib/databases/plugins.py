import functools

from bottle import request


def plugin(supervisor):
    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            request.db = supervisor.exts.databases
            return callback(*args, **kwargs)
        return wrapper
    return decorator
