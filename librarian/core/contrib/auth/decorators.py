import functools

from bottle import request


class PermissionDenied(Exception):
    """Exception being raised by helper functions if a user has no permission
    to access a resource."""
    pass


def permission_required(*permissions, user_getter=lambda: request.user,
                        denied_exception_class=PermissionDenied):
    """Decorator to protect a function from being invoked if the user that is
    trying to access it has no permission to do so. Usage:

    @permission_required(IsSecretService, IsBlessed, 'permission_name_also_ok')
    def your_func():
        return "secret"

    In case the user object is not on the request object itself, an optional
    `user_getter` parameter can specify a custom getter function which needs to
    return a user object when invoked.
    By default, if a permission is denied, the `PermissionDenied` exception
    will be raised. A custom exception class can be specified using the
    `denied_exception_class` parameter.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = user_getter()
            if all(map(user.has_permission, permissions)):
                return func(*args, **kwargs)

            if denied_exception_class:
                raise denied_exception_class()
            # deny access silently if that's what's needed
        return wrapper
    return decorator
