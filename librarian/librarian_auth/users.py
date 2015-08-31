"""
auth.py: User authentication and authorization

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools
import json

from bottle import request

from librarian.librarian_core.contrib.auth.acl import BaseUser

from .groups import Group
from .options import Options, DateTimeDecoder, DateTimeEncoder
from .utils import from_csv, to_csv


def authenticated_only(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.is_authenticated:
            return func(self, *args, **kwargs)
    return wrapper


class User(BaseUser):

    def __init__(self, username=None, password=None, reset_token=None,
                 created=None, options=None, groups=None, db=None):
        self.username = username
        self.password = password
        self.reset_token = reset_token
        self.created = created
        self.options = Options(options, onchange=self.save)
        self.db = db or request.db.sessions
        groups = [Group.from_name(name, db=db) for name in from_csv(groups)]
        super(User, self).__init__(groups=groups)

    @property
    def is_authenticated(self):
        return self.username is not None

    @property
    def is_superuser(self):
        return any([group.has_superpowers for group in self.groups])

    @authenticated_only
    def logout(self):
        request.session.delete().reset()
        request.user = User()

    @authenticated_only
    def save(self):
        query = self.db.Replace('users', cols=('username',
                                               'password',
                                               'reset_token',
                                               'created',
                                               'options',
                                               'groups'))
        self.db.query(query,
                      username=self.username,
                      password=self.password,
                      reset_token=self.reset_token,
                      created=self.created,
                      options=self.options.to_json(),
                      groups=to_csv([group.name for group in self.groups]))

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
