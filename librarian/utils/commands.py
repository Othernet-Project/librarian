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
        PARSER_ARGS.append((args, kwargs))
        return fn
    return registrator


@command('su', '--su', action='store_true', help='create superuser and quit')
def create_superuser(arg, db, config):
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


def add_command_switches(parser):
    for args, kwargs in PARSER_ARGS:
        parser.add_argument(*args, **kwargs)


def select_command(cmdargs, db, config):
    for cmd, fn in COMMANDS.items():
        if cmd not in cmdargs:
            continue
        arg = getattr(cmdargs, cmd)
        fn(arg, db, config)
