import datetime
import hashlib
import random
import string
import urllib
import urlparse

import pbkdf2

from bottle import request

from .groups import Group
from .users import User
from .utils import row_to_dict


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
    return ''.join([random.choice(string.digits) for i in range(length)])


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

    groups = [Group.from_name('superuser', db=db)] if is_superuser else []

    user_data = {'username': username,
                 'password': encrypted,
                 'reset_token': hashed_token,
                 'created': datetime.datetime.utcnow(),
                 'options': {},
                 'groups': groups}
    user = User(db=db, **user_data)
    user.save()


def get_user(username):
    db = request.db.sessions
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    user = db.result
    return row_to_dict(user) if user else {}


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
    if user and is_valid_password(password, user['password']):
        request.user = User(**user)
        request.session.rotate()
        return True

    return False
