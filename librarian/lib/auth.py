import datetime
import functools
import sqlite3
import urllib
import urlparse

import bottle
import pbkdf2


class UserAlreadyExists(Exception):
    pass


class InvalidUserCredentials(Exception):
    pass


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


def login_required(redirect_to='/login/', superuser_only=False,
                   forbidden_template='403'):
    def _login_required(func):
        @functools.wraps(func)
        def __login_required(*args, **kwargs):
            next_path = bottle.request.fullpath
            if bottle.request.query_string:
                next_path = '?'.join([bottle.request.fullpath,
                                      bottle.request.query_string])

            user = bottle.request.session.get('user')
            if user:
                is_superuser = user['is_superuser']
                if not superuser_only or (superuser_only and is_superuser):
                    return func(*args, **kwargs)

                return bottle.template(forbidden_template)

            redirect_path = get_redirect_path(redirect_to, next_path)
            return bottle.redirect(redirect_path)

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

    db = bottle.request.db
    query = db.Insert('users', cols=('username',
                                     'password',
                                     'created',
                                     'is_superuser'))
    try:
        db.execute(query, user_data)
    except sqlite3.IntegrityError:
        raise UserAlreadyExists()


def login_user(username, password):
    db = bottle.request.db
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    user = db.result

    if user and is_valid_password(password, user.password):
        bottle.request.session['user'] = {'username': user.username,
                                          'is_superuser': user.is_superuser}
        return True

    return False
