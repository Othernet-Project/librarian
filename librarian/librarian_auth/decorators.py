import functools

from bottle import abort, request, redirect

from .helpers import get_redirect_path


def login_required(redirect_to='/login/', superuser_only=False, next_to=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.no_auth:
                return func(*args, **kwargs)

            if next_to is None:
                next_path = request.fullpath
                if request.query_string:
                    next_path = '?'.join([request.fullpath,
                                          request.query_string])
            else:
                next_path = next_to

            if request.user.is_authenticated:
                is_superuser = request.user.is_superuser
                if not superuser_only or (superuser_only and is_superuser):
                    return func(*args, **kwargs)
                return abort(403)

            redirect_path = get_redirect_path(redirect_to, next_path)
            return redirect(redirect_path)
        return wrapper
    return decorator
