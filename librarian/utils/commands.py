"""
commands.py: Librarian commands

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import getpass

from ..lib import auth

COMMANDS = {}
PARSER_ARGS = []


def command(name, *args, **kwargs):
    def registrator(fn):
        COMMANDS[name] = fn
        if fn.__doc__:
            kwargs.setdefault('help', fn.__doc__.strip())
        PARSER_ARGS.append((args, kwargs))
        return fn
    return registrator


@command('su', '--su', action='store_true')
def create_superuser(arg, db, config):
    """ create superuser and quit """
    print("Press ctrl-c to abort")
    try:
        username = raw_input('Username: ')
        password = getpass.getpass()
    except KeyboardInterrupt:
        print("Aborted")
        sys.exit(1)

    try:
        auth.create_user(username=username,
                         password=password,
                         is_superuser=True,
                         db=db)
        print("User created.")
    except auth.UserAlreadyExists:
        print("User already exists, please try a different username.")
        create_superuser()
    except auth.InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser()

    sys.exit(0)


@command('dump_tables', '--dump-tables', action='store_true')
def dump_tables(arg, db, config):
    """ dump table schema as SQL """
    schema = []
    db.query(db.Select('*', sets='sqlite_master'))
    for r in db.results:
        if r.type == 'table':
            schema.append(r.sql)
    print('\n'.join(schema))
    sys.exit(0)


def add_command_switches(parser):
    for args, kwargs in PARSER_ARGS:
        parser.add_argument(*args, **kwargs)


def select_command(args, db, config):
    """ Select one of the registered commands and execute it """
    for cmd, fn in COMMANDS.items():
        arg = getattr(args, cmd, None)
        if arg:
            fn(arg, db, config)
