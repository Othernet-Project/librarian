import functools

from bottle import request


def identify_database(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs.pop('db', None) or request.db.auth  # mustn't evaluate
        return func(db=db, *args, **kwargs)
    return wrapper
