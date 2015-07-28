"""
auth.py: User authentication and authorization

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json
import urllib
import random
import sqlite3
import hashlib
import urlparse
import datetime
import functools

import pbkdf2
from bottle import request, abort, redirect, hook

from .options import Options, DateTimeDecoder, DateTimeEncoder


TOKEN_CHARS = '0123456789'


class UserAlreadyExists(Exception):
    pass


class InvalidUserCredentials(Exception):
    pass


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
            options = self.options.to_json()
            query = db.Update('users',
                              options=':options',
                              where='username = :username')
            db.query(query, username=self.username, options=options)

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


def set_password(username, clear_text):
    """ Set password using provided clear-text password """
    password = encrypt_password(clear_text)
    db = request.db.sessions
    query = db.Update('users', password=':password',
                      where='username = :username')
    db.query(query, password=password, username=username)


def generate_reset_token(length=6):
    # This token is not particularly secure, because the emphasis was on
    # convenience rather than security. It is reasonably easy to crack the
    # token.
    return ''.join([random.choice(TOKEN_CHARS) for i in range(length)])


def is_valid_password(password, encrypted_password):
    return encrypted_password == pbkdf2.crypt(password, encrypted_password)


def create_user(username, password, is_superuser=False, db=None,
                overwrite=False, reset_token=None):
    if not username or not password:
        raise InvalidUserCredentials()

    if not reset_token:
        reset_token = generate_reset_token()

    encrypted = encrypt_password(password)

    sha1 = hashlib.sha1()
    sha1.update(reset_token.encode('utf8'))
    hashed_token = sha1.hexdigest()

    user_data = {'username': username,
                 'password': encrypted,
                 'created': datetime.datetime.utcnow(),
                 'is_superuser': is_superuser,
                 'reset_token': hashed_token}

    db = db or request.db.sessions
    sql_cmd = db.Replace if overwrite else db.Insert
    query = sql_cmd('users', cols=('username',
                                   'password',
                                   'created',
                                   'is_superuser',
                                   'reset_token'))
    try:
        db.execute(query, user_data)
        return reset_token
    except sqlite3.IntegrityError:
        raise UserAlreadyExists()


def get_user(username):
    db = request.db.sessions
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    return db.result


def get_user_by_reset_token(token):
    sha1 = hashlib.sha1()
    sha1.update(token.encode('utf8'))
    hashed_token = sha1.hexdigest()
    db = request.db.sessions
    query = db.Select(sets='users', where='reset_token = ?')
    db.query(query, hashed_token)
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
    def process_options():
        if hasattr(request, 'session') and hasattr(request, 'user'):
            request.user.options.apply()
            request.session['user'] = request.user.to_json()

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            request.no_auth = no_auth
            user_data = request.session.get('user', '{}')
            request.user = User.from_json(user_data)
            return callback(*args, **kwargs)

        return wrapper
    plugin.name = 'user'
    return plugin
