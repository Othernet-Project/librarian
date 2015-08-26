"""
auth.py: User authentication and authorization

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json

from bottle import request

from .options import Options, DateTimeDecoder, DateTimeEncoder


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
