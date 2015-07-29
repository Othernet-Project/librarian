"""
commands.py: Librarian commands

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re
import sys
import pprint
import getpass

import hooks

from ..core.archive import Archive
from ..lib import auth
from ..utils import static
from .version import get_version


COMMANDS = {}
PARSER_ARGS = []


def command(name, *args, **kwargs):
    def registrator(fn):
        COMMANDS[name] = fn
        if fn.__doc__:
            kwargs.setdefault('help', fn.__doc__.strip())
        PARSER_ARGS.append((name, args, kwargs))
        return fn
    return registrator


def create_superuser(app):
    print("Press ctrl-c to abort")
    try:
        username = raw_input('Username: ')
        password = getpass.getpass()
    except (KeyboardInterrupt, EOFError):
        print("Aborted")
        sys.exit(1)

    try:
        reset_token = auth.create_user(
            username=username,
            password=password,
            is_superuser=True,
            db=app.databases.sessions,
            overwrite=True)
        print("User created. The password reset token is: {}".format(
            reset_token))
    except auth.UserAlreadyExists:
        print("User already exists, please try a different username.")
        create_superuser(app)
    except auth.InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser(app)

    sys.exit(0)


@command('su', '--su', action='store_true')
def create_superuser_command(arg, app):
    """ create superuser and quit """
    app.events.subscribe(hooks.START, create_superuser)


@command('debug_conf', '--debug-conf', action='store_true',
         help='print out the configuration in use and exit')
def debug_conf(arg, app):
    print('Configuration file path: %s' % app.args.conf)
    pprint.pprint(app.config, indent=4)
    sys.exit(0)


def dump_tables(app):
    schema = []
    for db in app.databases.values():
        db.query(db.Select('*', sets='sqlite_master'))
        for r in db.results:
            if r.type == 'table':
                schema.append(r.sql)
        print('\n'.join(schema))
    sys.exit(0)


@command('dump_tables', '--dump-tables', action='store_true')
def dump_tables_command(arg, app):
    """ dump table schema as SQL """
    app.events.subscribe(hooks.START, dump_tables)


def refill_db(app):
    print('Begin content refill.')
    archive = Archive.setup(app.config['librarian.backend'],
                            app.databases.main,
                            unpackdir=app.config['content.unpackdir'],
                            contentdir=app.config['content.contentdir'],
                            spooldir=app.config['content.spooldir'],
                            meta_filename=app.config['content.metadata'])
    archive.clear_and_reload()
    print('Content refill finished.')
    sys.exit(0)


@command('refill', '--refill', action='store_true',
         help="Empty database and then reload zipballs into it.")
def refill_command(arg, app):
    app.events.subscribe(hooks.START, refill_db)


def reload_db(app):
    print('Begin content reload.')
    archive = Archive.setup(app.config['librarian.backend'],
                            app.databases.main,
                            unpackdir=app.config['content.unpackdir'],
                            contentdir=app.config['content.contentdir'],
                            spooldir=app.config['content.spooldir'],
                            meta_filename=app.config['content.metadata'])
    archive.reload_content()
    print('Content reload finished.')
    sys.exit(0)


@command('reload', '--reload', action='store_true',
         help="Reload zipballs into database without clearing it previously.")
def reload_command(arg, app):
    app.events.subscribe(hooks.START, reload_db)


def repl_start(app):
    from .repl import start_repl
    namespace = dict(app=app)
    message = 'Press Ctrl-C to shut down Librarian.'
    app.repl_thread = start_repl(namespace, message)


def repl_shutdown(app):
    app.repl_thread.join()


@command('repl', '--repl', action='store_true',
         help='start interactive shell after servers start')
def repl(arg, app):
    app.events.subscribe(hooks.POST_START, repl_start)
    app.events.subscribe(hooks.SHUTDOWN, repl_shutdown)


@command('assets', '--assets', action='store_true',
         help='rebuild static assets')
def assets_command(arg, app):
    static.rebuild_assets(app.config)
    sys.exit(0)


@command('version', '--version', action='store_true',
         help='print out version number and exit')
def version(arg, app):
    ver = get_version(app.version, app.config)
    print('v%s' % ver)
    sys.exit(0)


def register_commands(parser, app):
    # conf is handled actually by a separate parser, but in order to show up
    # in help, it's added here as well
    parser.add_argument('--conf', metavar='PATH', default=app.CONFPATH,
                        help='path to configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='enable debugging')
    parser.add_argument('--log', metavar='PATH', default=None,
                        help='log file path (default: specified in .ini file)')
    parser.add_argument('--no-auth', action='store_true',
                        help='disable authentication')

    for (name, args, kwargs) in PARSER_ARGS:
        if name in app.config['librarian.commands']:
            parser.add_argument(*args, **kwargs)


def select_command(app):
    """ Select one of the registered commands and execute it """
    for name, fn in COMMANDS.items():
        arg = getattr(app.args, name, None)
        if arg:
            fn(arg, app)


def get_config_path():
    regex = r'--conf[=\s]{1}((["\']{1}(.+)["\']{1})|([^\s]+))\s*'
    arg_str = ' '.join(sys.argv[1:])
    result = re.search(regex, arg_str)
    return result.group(1).strip(' \'"') if result else None
