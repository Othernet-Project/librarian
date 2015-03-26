import datetime
import functools
import json
import sqlite3
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


class UserAlreadyExists(Exception):
    pass


class InvalidUserCredentials(Exception):
    pass


class Session(object):

    def __init__(self, session_id, data, expires):
        self.id = session_id
        self.data = json.loads(data)
        self.expires = expires

    @classmethod
    def fetch(cls, session_id):
        """Fetch an existing session by it ID.

        :param session_id:  Unique session ID
        :returns:           Valid `Session` instance.
        """
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
        """Create a new session.

        :param lifetime:  Session lifetime in seconds.
        :returns:         Valid `Session` instance.
        """
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

    def save(self):
        """Store current session in database."""
        session_data = {'session_id': self.id,
                        'data': json.dumps(self.data),
                        'expires': self.expires}
        db = bottle.request.db
        query = db.Replace('sessions', cols=('session_id', 'data', 'expires'))
        db.execute(query, session_data)

    def __contains__(self, key):
        """Check if a key is in the session dictionary.

        :param key:  The dictionary key.
        :returns:    bool
        """
        return key in self.data

    def __delitem__(self, key):
        """Delete an item from the session dictionary.

        param key:  The dictionary key.
        """
        del self.data[key]

    def __getitem__(self, key):
        """Return a value associated with a key from the session dictionary.

        :param key:  The dictionary key.
        :returns:    The value associated with that key in the dictionary.
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """Set a key-value association.

        :param key:    The dictionary key.
        :param value:  The dictionary value
        """
        self.data[key] = value

    def __len__(self):
        """Get the number of key-value pairs in the session dictionary.

        :returns:  Number of key value pairs in the dictionary.
        """
        return len(self.data)

    def __iter__(self):
        """Iterate over the dictionary keys.

        :yields:  Dictionary keys
        """
        for key in self.data.items():
            yield key

    def get(self, key, default=None):
        """Get a value from the dictionary.

        :param key:      The dictionary key.
        :param default:  The default to return if the key is not in the
                          dictionary. Defaults to None.
        :returns:         The dictionary value or the default if the key is not
                          in the dictionary.
        """
        return self.data.get(key, default)

    def has_key(self, key):
        """Check if the dictionary contains a key.

        :param key:  The dictionary key.
        :returns:     bool
        """
        return self.__contains__(key)

    def items(self):
        """Return a list of all the key-value pair tuples in the session dict.

        :returns:  list of tuples
        """
        return self.data.items()

    def keys(self):
        """Return a list of all keys in the session dictionary.

        :returns:  list of str
        """
        return self.data.keys()

    def values(self):
        """Returns a list of all values in the session dictionary.

        :returns:  list of values
        """
        return self.data.values()


def session_plugin(cookie_name, lifetime, secret):
    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            session_id = bottle.request.get_cookie(cookie_name, secret=secret)
            try:
                bottle.request.session = Session.fetch(session_id)
            except (SessionExpired, SessionInvalid):
                bottle.request.session = Session.create(lifetime)

            bottle.response.set_cookie(cookie_name,
                                       bottle.request.session.id,
                                       path='/',
                                       secret=secret,
                                       max_age=lifetime)

            result = callback(*args, **kwargs)
            bottle.request.session.save()
            return result

        return wrapper
    return plugin


def login_required(redirect_to='/login/', superuser_only=False,
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
        bottle.request.session['user'] = user
        return True

    return False
