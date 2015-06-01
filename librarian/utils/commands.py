"""
commands.py: Librarian commands

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import getpass

from .. import __version__
from ..core.archive import Archive
from ..lib import auth
from .version import full_version_info


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
def create_superuser(arg, databases, config):
    """ create superuser and quit """
    print("Press ctrl-c to abort")
    try:
        username = raw_input('Username: ')
        password = getpass.getpass()
    except (KeyboardInterrupt, EOFError):
        print("Aborted")
        sys.exit(1)

    try:
        auth.create_user(username=username,
                         password=password,
                         is_superuser=True,
                         db=databases.sessions,
                         overwrite=True)
        print("User created.")
    except auth.UserAlreadyExists:
        print("User already exists, please try a different username.")
        create_superuser(arg, databases, config)
    except auth.InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser(arg, databases, config)

    sys.exit(0)


@command('dump_tables', '--dump-tables', action='store_true')
def dump_tables(arg, databases, config):
    """ dump table schema as SQL """
    schema = []
    for db in databases.values():
        db.query(db.Select('*', sets='sqlite_master'))
        for r in db.results:
            if r.type == 'table':
                schema.append(r.sql)
        print('\n'.join(schema))
    sys.exit(0)


@command('refill', '--refill', action='store_true',
         help="Empty database and then reload zipballs into it.")
def refill_command(arg, databases, config):
    print('Begin content refill.')
    archive = Archive.setup(config['librarian.backend'],
                            databases.main,
                            unpackdir=config['content.unpackdir'],
                            contentdir=config['content.contentdir'],
                            spooldir=config['content.spooldir'],
                            meta_filename=config['content.metadata'])
    archive.clear_and_reload()
    print('Content refill finished.')
    sys.exit(0)


@command('reload', '--reload', action='store_true',
         help="Reload zipballs into database without clearing it previously.")
def reload_command(arg, databases, config):
    print('Begin content reload.')
    archive = Archive.setup(config['librarian.backend'],
                            databases.main,
                            contentdir=config['content.contentdir'],
                            spooldir=config['content.spooldir'],
                            meta_filename=config['content.metadata'])
    archive.reload_data()
    print('Content reload finished.')
    sys.exit(0)


@command('version', '--version', action='store_true',
         help='print out version number and exit')
def version(arg, databases, config):
    ver = full_version_info(__version__, config)
    print('v%s' % ver)
    sys.exit()


def add_command_switches(parser):
    for args, kwargs in PARSER_ARGS:
        parser.add_argument(*args, **kwargs)


def select_command(args, databases, config):
    """ Select one of the registered commands and execute it """
    for cmd, fn in COMMANDS.items():
        arg = getattr(args, cmd, None)
        if arg:
            fn(arg, databases, config)
