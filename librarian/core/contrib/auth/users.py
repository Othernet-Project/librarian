import functools
import hashlib
import json
import re

import pbkdf2

from bottle import request

from ..databases.serializers import DateTimeDecoder, DateTimeEncoder
from ..databases.utils import utcnow, from_csv, to_csv, row_to_dict

from .base import BaseUser
from .groups import Group
from .helpers import identify_database
from .options import Options
from .utils import generate_random_key


USERNAME_REGEX = re.compile(r'^\S{1,12}$')


def authenticated_only(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.is_authenticated:
            return func(self, *args, **kwargs)
    return wrapper


class InvalidUserCredentials(Exception):
    pass


class User(BaseUser):

    InvalidUserCredentials = InvalidUserCredentials

    @identify_database
    def __init__(self, username=None, password=None, reset_token=None,
                 created=None, options=None, groups=None, db=None):
        self.username = username
        self.password = password
        self.reset_token = reset_token
        self.created = created
        self.options = Options(options, onchange=self.save)
        self.db = db
        groups = [Group.from_name(name, db=db) for name in from_csv(groups)]
        super(User, self).__init__(groups=groups)

    @property
    def is_authenticated(self):
        return self.username is not None

    @property
    def is_superuser(self):
        return any([group.has_superpowers for group in self.groups])

    def get_permission_kwargs(self):
        return dict(identifier=self.username, db=self.db)

    @authenticated_only
    def logout(self):
        request.session.delete().reset()
        request.user = User(db=self.db)

    @authenticated_only
    def save(self):
        query = self.db.Replace('users',
                                constraints=['username'],
                                cols=('username',
                                      'password',
                                      'reset_token',
                                      'created',
                                      'options',
                                      'groups'))
        data = dict(username=self.username,
                    password=self.password,
                    reset_token=self.reset_token,
                    created=self.created,
                    options=self.options.to_json(),
                    groups=to_csv([group.name for group in self.groups]))
        self.db.execute(query, data)

    def to_json(self):
        data = dict(username=self.username,
                    password=self.password,
                    reset_token=self.reset_token,
                    created=self.created,
                    options=self.options.to_native(),
                    groups=to_csv([group.name for group in self.groups]))
        return json.dumps(data, cls=DateTimeEncoder)

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data, cls=DateTimeDecoder))

    @classmethod
    @identify_database
    def from_username(cls, username, db):
        query = db.Select(sets='users', where='username = %s')
        user = db.fetchone(query, (username,))
        if user is None:
            return None
        return cls(**row_to_dict(user))

    @classmethod
    @identify_database
    def from_group(cls, group, db):
        query = db.Select(sets='users', where='groups = %s')
        users = db.fetchall(query, (group,))
        if users is None:
            return None
        return [cls(**row_to_dict(user)) for user in users]

    @classmethod
    @identify_database
    def from_reset_token(cls, token, db):
        sha1 = hashlib.sha1()
        sha1.update(token.encode('utf8'))
        hashed_token = sha1.hexdigest()
        query = db.Select(sets='users', where='reset_token = %s')
        user = db.fetchone(query, (hashed_token,))
        if user is None:
            return None
        return cls(**row_to_dict(user))

    @classmethod
    @identify_database
    def create(cls, username, password, is_superuser=False, db=None,
               reset_token=None):
        if not USERNAME_REGEX.match(username) or not password:
            raise InvalidUserCredentials()

        if not reset_token:
            # This token is not particularly secure, because the emphasis was
            # on convenience rather than security. It is reasonably easy to
            # crack the token.
            reset_token = cls.generate_reset_token()

        encrypted = cls.encrypt_password(password)

        sha1 = hashlib.sha1()
        sha1.update(reset_token.encode('utf8'))
        hashed_token = sha1.hexdigest()

        groups = 'superuser' if is_superuser else ''

        user_data = {'username': username,
                     'password': encrypted,
                     'reset_token': hashed_token,
                     'created': utcnow(),
                     'options': {},
                     'groups': groups}
        user = cls(db=db, **user_data)
        user.save()
        return user

    @classmethod
    @identify_database
    def login(cls, username, password, db):
        username = (username or '').strip()
        password = (password or '').strip()
        user = cls.from_username(username, db=db)
        if user and cls.is_valid_password(password, user.password):
            request.user = user
            request.session.rotate()
            return user

        return False

    @classmethod
    @identify_database
    def set_password(cls, username, clear_text, db):
        """ Set password using provided clear-text password """
        password = cls.encrypt_password(clear_text)
        query = db.Update('users',
                          password='%(password)s',
                          where='username = %(username)s')
        db.execute(query, dict(username=username, password=password))

    @staticmethod
    def encrypt_password(password):
        return pbkdf2.crypt(password)

    @staticmethod
    def is_valid_password(password, encrypted_password):
        return encrypted_password == pbkdf2.crypt(password, encrypted_password)

    @staticmethod
    def generate_reset_token():
        return generate_random_key(letters=False,
                                   digits=True,
                                   punctuation=False,
                                   length=6)
