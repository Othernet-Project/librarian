"""
security.py: security related utilities

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import random
import string

from ..lib import auth
from ..lib import sessions

from .setup import autoconfigure


def generate_secret_key(length=50):
    charset = [string.ascii_letters, string.digits, string.punctuation]
    chars = (''.join(charset).replace('\'', '')
                             .replace('"', '')
                             .replace('\\', ''))
    return ''.join([random.choice(chars) for i in range(length)])


def auto_setup(app):
    # register session and csrf secret auto configurator
    autoconfigure('session.secret')(generate_secret_key)
    autoconfigure('csrf.secret')(generate_secret_key)


def session_plugin(app):
    app.install(sessions.session_plugin(
        cookie_name=app.config['session.cookie_name'],
        secret=app.config['session.secret']
    ))


def auth_plugin(app):
    app.install(auth.user_plugin(app.args.no_auth))
