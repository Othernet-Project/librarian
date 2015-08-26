"""
commands.py: Librarian commands

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


'''
@command('debug_conf', '--debug-conf', action='store_true',
         help='print out the configuration in use and exit')
def debug_conf(arg, app):
    print('Configuration file path: %s' % app.args.conf)
    pprint.pprint(app.config, indent=4)
    sys.exit(0)


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


@command('version', '--version', action='store_true',
         help='print out version number and exit')
def version(arg, app):
    ver = get_version(app.version, app.config)
    print('v%s' % ver)
    sys.exit(0)


def register_commands(parser, app):
    # conf is handled actually by a separate parser, but in order to show up
    # in help, it's added here as well
    parser.add_argument('--log', metavar='PATH', default=None,
                        help='log file path (default: specified in .ini file)')
'''
