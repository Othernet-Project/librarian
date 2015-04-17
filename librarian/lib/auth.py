"""
auth.py: User authentication and authorization

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import copy
import datetime
import functools
import json
import sqlite3
import urllib
import urlparse

import pbkdf2
from bottle import request, abort, redirect, hook


class UserAlreadyExists(Exception):
    pass


class InvalidUserCredentials(Exception):
    pass


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return super(DateTimeEncoder, self).default(obj)


class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        super(DateTimeDecoder, self).__init__(object_hook=self.object_hook,
                                              *args,
                                              **kargs)

    def object_hook(self, obj):
        if '__type__' not in obj:
            return obj

        obj_type = obj.pop('__type__')
        try:
            return datetime(**obj)
        except Exception:
            obj['__type__'] = obj_type
            return obj


class Options(object):
    """A dict-like object with a callback that is invoked when changes are made
    to the object's state."""
    def __init__(self, data, onchange):
        self.onchange = onchange
        if isinstance(data, dict):
            self.__data = data
        else:
            self.__data = json.loads(data or '{}')

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def items(self):
        return self.__data.items()

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value
        self.onchange()

    def __contains__(self, key):
        return key in self.__data

    def __delitem__(self, key):
        del self.__data[key]
        self.onchange()

    def __len__(self):
        return len(self.__data)

    def to_json(self):
        return json.dumps(self.__data)

    def to_native(self):
        return copy.copy(self.__data)


class User(object):

    def __init__(self, username=None, is_superuser=None, created=None,
                 options=None):
        self.username = username
        self.is_superuser = is_superuser
        self.created = created
        self.options = Options(options, onchange=self.save_options)

    @property
    def is_authenticated(self):
        return self.username is not None

    def save_options(self):
        if self.is_authenticated:
            db = request.db.sessions
            query = db.Update('users',
                              options=':options',
                              where='username = :username')
            db.query(query,
                     username=self.username,
                     options=self.options.to_json())

    def logout(self):
        if self.is_authenticated:
            request.session.delete().reset()
            request.user = User()

    def to_json(self):
        data = dict(username=self.username,
                    is_superuser=self.is_superuser,
                    created=self.created,
                    options=self.options.to_native())
        return json.dumps(data, cls=DateTimeEncoder)

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data, cls=DateTimeDecoder))


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


def encrypt_password(password):
    return pbkdf2.crypt(password)


def is_valid_password(password, encrypted_password):
    return encrypted_password == pbkdf2.crypt(password, encrypted_password)


def create_user(username, password, is_superuser=False, db=None):
    if not username or not password:
        raise InvalidUserCredentials()

    encrypted = encrypt_password(password)

    user_data = {'username': username,
                 'password': encrypted,
                 'created': datetime.datetime.utcnow(),
                 'is_superuser': is_superuser}

    db = db or request.db.sessions
    query = db.Insert('users', cols=('username',
                                     'password',
                                     'created',
                                     'is_superuser'))
    try:
        db.execute(query, user_data)
    except sqlite3.IntegrityError:
        raise UserAlreadyExists()


def get_user(username):
    db = request.db.sessions
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    return db.result


def login_user(username, password):
    user = get_user(username)
    if user and is_valid_password(password, user.password):
        request.user = User(username=user.username,
                            is_superuser=user.is_superuser,
                            created=user.created,
                            options=user.options)
        request.session.rotate()
        return True

    return False


def user_plugin(no_auth):
    # Set up a hook, so handlers that raise cannot escape session-saving
    @hook('after_request')
    def store_options():
        if hasattr(request, 'session'):
            request.session['user'] = request.user.to_json()

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            request.no_auth = no_auth
            user_data = request.session.get('user', '{}')
            request.user = User.from_json(user_data)
            return callback(*args, **kwargs)

        return wrapper
    return plugin
