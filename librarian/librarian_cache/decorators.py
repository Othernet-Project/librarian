import functools

from bottle import request

from .utils import is_string, generate_key


def cached(prefix='', timeout=None):
    """Decorator that caches return values of functions that it wraps. The
    key is generated from the function's name and the parameters passed to
    it. E.g.:

    @cached(timeout=300)  # expires in 5 minutes
    def my_func(a, b, c=4):
        return (a + b) / c

    Cache key in this case is an md5 hash, generated from the combined
    values of: function's name("my_func"), and values of `a`, `b` and in
    case of keyword arguments both argument name "c" and the value of `c`,
    prefix with the value of the `prefix` keyword argument.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.app.supervisor.exts.is_installed('cache'):
                return func(*args, **kwargs)

            backend = request.app.supervisor.exts.cache
            generated = generate_key(func.__name__, *args, **kwargs)
            parsed_prefix = backend.parse_prefix(prefix)
            key = '{0}{1}'.format(parsed_prefix, generated)
            value = backend.get(key)
            if value is None:
                # not found in cache, or is expired, recalculate value
                value = func(*args, **kwargs)
                expires_in = timeout
                if expires_in is None:
                    expires_in = backend.default_timeout
                backend.set(key, value, timeout=expires_in)
            return value
        return wrapper
    return decorator


def invalidates(prefix, before=False, after=False):
    """Decorator that invalidates keys matching the specified prefix(es) before
    and/or after invoking the wrapped function."""

    def invalidate_prefixes(prefixes):
        """Helper function to call invalidate over a list of prefixes."""
        for p in prefixes:
            request.app.supervisor.exts.cache.invalidate(prefix=p)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # make sure we're working with a list of prefixes always
            prefixes = [prefix] if is_string(prefix) else prefix
            if before:
                # invalidate cache before invoking wrapped function
                invalidate_prefixes(prefixes)
            # obtain result of wrapped function
            result = func(*args, **kwargs)
            if after:
                # invalidate cache after invoking wrapped function
                invalidate_prefixes(prefixes)
            # return result of wrapped function
            return result
        return wrapper
    return decorator
