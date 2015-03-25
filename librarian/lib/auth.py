import datetime
import functools
import json
import uuid

import bottle
import pbkdf2


class SessionError(Exception):

    def __init__(self, session_id):
        super(SessionError, self).__init__()
        self.session_id = session_id


class SessionInvalid(SessionError):
    pass


class SessionExpired(SessionError):
    pass


class Session(object):

    def __init__(self, session_id, data, expires):
        self.id = session_id
        self.data = json.loads(data)
        self.expires = expires

    @classmethod
    def get(cls, session_id):
        db = bottle.request.db
        query = db.Select(sets='sessions', where='session_id = ?')
        db.query(query, session_id)
        session_data = db.result

        if not session_data:
            raise SessionInvalid(session_id)

        if session_data.expires < datetime.datetime.utcnow():
            raise SessionExpired(session_id)

        return cls(**session_data)

    @classmethod
    def generate_session_id(cls):
        return uuid.uuid4().hex

    @classmethod
    def create(cls, lifetime):
        session_id = cls.generate_session_id()
        data = {}
        expires_in = datetime.timedelta(seconds=lifetime)
        expires = datetime.datetime.utcnow() + expires_in

        session_data = {'session_id': session_id,
                        'data': json.dumps(data),
                        'expires': expires}

        db = bottle.request.db
        query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
        db.execute(query, session_data)
        return cls(**session_data)


def session_plugin(cookie_name, lifetime, secret):
    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            session_id = bottle.request.get_cookie(cookie_name, secret=secret)
            try:
                bottle.request.session = Session.get(session_id)
            except (SessionExpired, SessionInvalid):
                bottle.request.session = Session.create(lifetime)

            bottle.response.set_cookie(cookie_name,
                                       bottle.request.session.id,
                                       path='/',
                                       secret=secret,
                                       max_age=lifetime)

            return callback(*args, **kwargs)
        return wrapper
    return plugin


def login_required(redirect_to='/login', superuser_only=False,
                   forbidden_template='403'):
    def _login_required(func):
        @functools.wraps(func)
        def __login_required(*args, **kwargs):
            user = bottle.request.session.get('user')
            if user:
                is_superuser = user['is_superuser']
                if not superuser_only or (superuser_only and is_superuser):
                    return func(*args, **kwargs)

                return bottle.template(forbidden_template)

            return bottle.redirect(redirect_to)

        return __login_required
    return _login_required


def encrypt_password(password):
    return pbkdf2.crypt(password)


def is_valid_password(password, encrypted_password):
    return encrypted_password == pbkdf2.crypt(password, encrypted_password)


def create_user(username, password, is_superuser=False):
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
    db.execute(query, user_data)
