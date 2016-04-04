import functools

from bottle import request

from .notifications import Notification


def notifies(message, **params):
    """Decorator that creates a notification upon the successful return of it's
    wrapped function. E.g.:

    @notifies("They're together",
              category="joined",
              user=lambda: request.user.username)
    def join(a, b):
        return a + b

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if request.app.supervisor.exts.is_installed('notifications'):
                options = dict((name, value() if callable(value) else value)
                               for name, value in params.items())
                Notification.send(message=message, **options)

            return result
        return wrapper
    return decorator
