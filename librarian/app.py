# -*- coding: utf-8 -*-

"""
app.py: main web UI module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals, print_function

import gevent.monkey
gevent.monkey.patch_all(aggressive=True)

# For more details on the below see: http://bit.ly/18fP1uo
import gevent.hub
gevent.hub.Hub.NOT_ERROR = (Exception,)

import argparse
import sys
import time
import logging
from os.path import join, dirname, abspath, normpath

import bottle

from bottle_utils.i18n import I18NPlugin

from librarian.lib.confloader import ConfDict

from librarian.utils import exts
from librarian.utils import lang
from librarian.utils import hooks
from librarian.utils import pubsub
from librarian.utils import version
from librarian.utils import commands
from librarian.utils.gserver import ServerManager
from librarian.utils.signal_handlers import on_interrupt

from librarian import __version__

MODDIR = dirname(abspath(__file__))


def in_pkg(*paths):
    """ Return path relative to module directory """
    return normpath(join(MODDIR, *paths))


servers = ServerManager()

app = bottle.default_app()
app.events = pubsub.PubSub()
app.exts = exts.ExtContainer()
app.in_pkg = in_pkg

app.CONFPATH = in_pkg('librarian.ini')


def prestart():
    bottle.debug(app.args.debug or app.config['librarian.debug'])
    logging.info('Configuring Librarian environment')
    app.events.publish(hooks.PRE_START, app)
    logging.info("Finished Librarian configuration")


def start():
    """ Start the application """
    logging.info('===== Starting Librarian v%s =====', app.version)
    # We are passing the ``wsgiapp`` object here because that's the one that
    # contains the I18N middleware. If we pass ``app`` object, then we won't
    # have the I18N middleware active at all.
    default_locale = app.config.get('language', lang.DEFAULT_LOCALE)
    wsgiapp = I18NPlugin(app,
                         langs=lang.UI_LANGS,
                         default_locale=default_locale,
                         domain='librarian',
                         locale_dir=app.in_pkg('locales'))
    # run start hooks
    app.events.publish(hooks.START, app)
    # Start the server
    servers.start_server('librarian', app.config, wsgiapp)
    # run post-start hooks
    app.events.publish(hooks.POST_START, app)
    # register interrupt handler
    on_interrupt(shutdown)
    print('Press Ctrl-C to shut down Librarian.')
    try:
        while True:
            # run background hooks
            app.events.publish(hooks.BACKGROUND, app)
            time.sleep(10)
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt received')
    return shutdown()


def shutdown(*args, **kwargs):
    """ Cleanly shut down the server """
    logging.info('Librarian is going down.')
    # run shutdown hooks
    app.events.publish(hooks.SHUTDOWN, app)
    # stop all servers
    servers.stop_all(5)
    logging.info('Clean shutdown completed')
    print('Bye! Have a nice day! Those books are due Tuesday, by the way!')


def main():
    config_path = commands.get_config_path() or app.CONFPATH
    app.config = ConfDict.from_file(config_path, catchall=True, autojson=True)
    app.version = version.get_version(__version__, app.config)
    hooks.register_hooks(app)
    # register command line arg handlers
    parser = argparse.ArgumentParser()
    app.events.publish(hooks.COMMANDS, parser, app)
    # parse command line args
    app.args = parser.parse_args(sys.argv[1:])
    commands.select_command(app)
    # begin app-start sequence
    prestart()
    sys.exit(start())


if __name__ == '__main__':
    main()
