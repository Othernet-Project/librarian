import functools

from ...exts import ext_container as exts


def identify_database(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs.pop('db', exts.databases.auth)
        return func(db=db, *args, **kwargs)
    return wrapper
