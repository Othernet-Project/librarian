import datetime
import functools
import sqlite3
import urllib
import urlparse

import pbkdf2
from bottle import request, abort, redirect


class UserAlreadyExists(Exception):
    pass


class InvalidUserCredentials(Exception):
    pass


class User(object):

    def __init__(self, username=None, is_superuser=None, created=None):
        self.username = username
        self.is_superuser = is_superuser
        self.created = created

    @property
    def is_authenticated(self):
        return self.username is not None

    def logout(self):
        if self.is_authenticated:
            request.session.destroy()
            request.user = User()


def get_redirect_path(base_path, next_path, next_param_name='next'):
    QUERY_PARAM_IDX = 4

    next_encoded = urllib.urlencode({next_param_name: next_path})

    parsed = urlparse.urlparse(base_path)
    new_path = list(parsed)

    if parsed.query:
        new_path[QUERY_PARAM_IDX] = '&'.join([new_path[QUERY_PARAM_IDX],
                                              next_encoded])
    else:
        new_path[QUERY_PARAM_IDX] = next_encoded

    return urlparse.urlunparse(new_path)


def login_required(redirect_to='/login/', superuser_only=False):
    def _login_required(func):
        @functools.wraps(func)
        def __login_required(*args, **kwargs):
            if not hasattr(request, 'user'):
                return func(*args, **kwargs)

            next_path = request.fullpath
            if request.query_string:
                next_path = '?'.join([request.fullpath,
                                      request.query_string])

            if request.user.is_authenticated:
                is_superuser = request.user.is_superuser
                if not superuser_only or (superuser_only and is_superuser):
                    return func(*args, **kwargs)
                abort(403)

            redirect_path = get_redirect_path(redirect_to, next_path)
            return redirect(redirect_path)

        return __login_required
    return _login_required


def encrypt_password(password):
    return pbkdf2.crypt(password)


def is_valid_password(password, encrypted_password):
    return encrypted_password == pbkdf2.crypt(password, encrypted_password)


def create_user(username, password, is_superuser=False):
    if not username or not password:
        raise InvalidUserCredentials()

    encrypted = encrypt_password(password)

    user_data = {'username': username,
                 'password': encrypted,
                 'created': datetime.datetime.utcnow(),
                 'is_superuser': is_superuser}

    db = request.db
    query = db.Insert('users', cols=('username',
                                     'password',
                                     'created',
                                     'is_superuser'))
    try:
        db.execute(query, user_data)
    except sqlite3.IntegrityError:
        raise UserAlreadyExists()


def get_user(username):
    db = request.db
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    return db.result


def login_user(username, password):
    user = get_user(username)
    if user and is_valid_password(password, user.password):
        request.session['user'] = {'username': user.username,
                                          'is_superuser': user.is_superuser}
        request.session.rotate()
        return True

    return False


def user_plugin():
    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            user_data = request.session.get('user') or {}
            if user_data:
                user = get_user(user_data.get('username'))
                user_data = dict(username=user.username,
                                 is_superuser=user.is_superuser,
                                 created=user.created) if user else {}

            request.user = User(**user_data)
            return callback(*args, **kwargs)

        return wrapper
    return plugin
