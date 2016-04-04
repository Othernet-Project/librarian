import functools
import urllib
import urlparse

from bottle import abort, request, redirect


def login_required(redirect_to='/login/', superuser_only=False, next_to=None):
    def get_redirect_path(base_path, next_path, next_param_name='next'):
        QUERY_PARAM_IDX = 4
        next_encoded = urllib.urlencode({next_param_name: next_path})
        parsed = urlparse.urlparse(base_path)
        new_path = list(parsed)
        # filter will drop falsey values
        params = filter(None, [new_path[QUERY_PARAM_IDX], next_encoded])
        new_path[QUERY_PARAM_IDX] = '&'.join(params)
        return urlparse.urlunparse(new_path)

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
