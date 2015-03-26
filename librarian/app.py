# -*- coding: utf-8 -*-

"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals, print_function

import gevent.monkey
gevent.monkey.patch_all(aggressive=True)

# For more details on the below see: http://bit.ly/18fP1uo
import gevent.hub
gevent.hub.Hub.NOT_ERROR=(Exception,)

import getpass
import sys
import pprint
import logging
from logging.config import dictConfig as log_config
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request

from librarian.core.metadata import LICENSES
from librarian.core.downloads import get_zipballs

from librarian.lib import squery
from librarian.lib import auth
from librarian.lib import session
from librarian.lib.lazy import Lazy
from librarian.lib import html as helpers
from librarian.lib.lock import lock_plugin
from librarian.lib.common import to_unicode
from librarian.lib.i18n import lazy_gettext as _, I18NPlugin

from librarian.utils import lang
from librarian.utils import migrations
from librarian.utils.system import ensure_dir
from librarian.utils.routing import add_routes
from librarian.utils.timer import request_timer

from librarian.plugins import install_plugins

from librarian.routes import (content, tags, downloads, apps, dashboard,
                              system, auth as auth_route)

from librarian import __version__

MODDIR = dirname(abspath(__file__))


def in_pkg(*paths):
    """ Return path relative to module directory """
    return normpath(join(MODDIR, *paths))


CONFPATH = in_pkg('librarian.ini')

# Routing table
#
# Each route is in following format::
#
#     (name, callback,
#      method, path, route_config_dict),
#
ROUTES = (

    # Authentication
    ('auth:login', auth_route.login,
     ['GET', 'POST'], '/login/', {}),

    # Content

    ('content:list', content.content_list,
     'GET', '/', {}),
    ('content:file', content.content_file,
     'GET', '/pages/<content_id>/<filename:path>', dict(no_i18n=True)),
    ('content:zipball', content.content_zipball,
     'GET', '/pages/<content_id>.zip', dict(no_i18n=True, unlocked=True)),
    ('content:reader', content.content_reader,
     'GET', '/pages/<content_id>', {}),
    ('content:cover', content.cover_image,
     'GET', '/covers/<path>', dict(no_i18n=True)),
    ('content:delete', content.remove_content,
     'POST', '/delete/<content_id>', {}),

    # Files

    ('files:list', content.show_file_list,
     'GET', '/files/', dict(unlocked=True)),
    ('files:path', content.show_file_list,
     'GET', '/files/<path:path>', dict(unlocked=True)),
    ('files:action', content.handle_file_action,
     'POST', '/files/<path:path>', dict(unlocked=True)),

    # Tags

    ('tags:list', tags.tag_cloud,
     'GET', '/tags/', {}),
    ('tags:edit', tags.edit_tags,
     'POST', '/tags/<content_id>', {}),

    # Downloads (Updates)

    ('downloads:list', downloads.list_downloads,
     'GET', '/downloads/', {}),
    ('downloads:action', downloads.manage_downloads,
     'POST', '/downloads/', {}),

    # Dashboard

    ('dashboard:main', dashboard.dashboard,
     'GET', '/dashboard/', {}),

    # Apps

    ('apps:list', apps.show_apps,
     'GET', '/apps/', dict(unlocked=True)),
    ('apps:app', apps.send_app_file,
     'GET', '/apps/<appid>/', dict(unlocked=True)),
    ('apps:asset', apps.send_app_file,
     'GET', '/apps/<appid>/<path:path>', dict(unlocked=True)),

    # System

    ('sys:static', system.send_static,
     'GET', '/static/<path:path>', dict(no_i18n=True, unlocked=True)),
    ('sys:logs', system.send_logfile,
     'GET', '/librarian.log', dict(no_i18n=True, unlocked=True)),
)

app = bottle.default_app()
add_routes(app, ROUTES)
app.error(500)(system.show_error_page)
app.error(503)(system.show_maint_page)


def start(logfile=None, profile=False):
    """ Start the application """

    config = app.config

    log_config({
        'version': 1,
        'root': {
            'handlers': ['file'],
            'level': logging.DEBUG,
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': logfile or config['logging.output'],
                'maxBytes': int(config['logging.size']),
                'backupCount': int(config['logging.backups'])
            },
        },
        'formatters': {
            'default': {
                'format': config['logging.format'],
                'datefmt': config['logging.date_format']
            },
        },
    })

    # Srart the server
    logging.info('===== Starting Librarian v%s =====', __version__)

    # Make sure all necessary directories are present
    ensure_dir(dirname(config['logging.output']))
    ensure_dir(dirname(config['database.path']))
    ensure_dir(config['content.spooldir'])
    ensure_dir(config['content.appdir'])
    ensure_dir(config['content.contentdir'])
    ensure_dir(config['content.covers'])

    # Run database migrations
    conn = squery.Database.connect(config['database.path'])
    db = squery.Database(conn)
    migrations.migrate(db, in_pkg('migrations'), 'librarian.migrations',
                       config)
    logging.debug("Finished running migrations")

    # Install Librarian plugins
    install_plugins(app)
    logging.info('Installed all plugins')

    # Install bottle plugins
    app.install(request_timer('Handler'))
    app.install(squery.database_plugin(conn, debug=True))
    app.install(session.session_plugin(
        cookie_name=config['session.cookie_name'],
        lifetime=int(config['session.lifetime']),
        secret=config['session.secret'])
    )

    # Set some basic configuration
    bottle.TEMPLATE_PATH.insert(0, in_pkg('views'))
    bottle.BaseTemplate.defaults.update({
        'app_version': __version__,
        'request': request,
        # Translators, used as default page title
        'title': _('Librarian'),
        'style': 'screen',  # Default stylesheet
        'h': helpers,
        'updates': Lazy(lambda: len(list(get_zipballs()))),
        'readable_license': lambda s: dict(LICENSES).get(s, LICENSES[0][1]),
        'is_rtl': Lazy(lambda: request.locale in lang.RTL_LANGS),
        'dir': lambda l: 'rtl' if l in lang.RTL_LANGS else 'auto',
        'LANGS': lang.LANGS,
        'UI_LANGS': lang.UI_LANGS,
        'SELECT_LANGS': lang.SELECT_LANGS,
        'u': to_unicode,
        'url': app.get_url,
    })

    # Add middlewares
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
    wsgiapp = I18NPlugin(wsgiapp, langs=lang.UI_LANGS,
                         default_locale=lang.DEFAULT_LOCALE,
                         domain='librarian', locale_dir=in_pkg('locales'))
    app.install(lock_plugin)
    app.install(request_timer('Total'))

    if profile:
        # Instrument the app to perform profiling
        print('Profiling enabled')
        from repoze.profile import ProfileMiddleware
        wsgiapp = ProfileMiddleware(
            wsgiapp,
            log_filename=config['profiling.logfile'],
            cachegrind_filename=config['profiling.outfile'],
            discard_first_request=True,
            flush_at_shutdown=True,
            path='/__profile__',
            unwind=False,
        )

    bottle.debug(config['librarian.debug'] == 'yes')
    print('Starting %s server <http://%s:%s/>' % (
        config['librarian.server'],
        config['librarian.bind'],
        config['librarian.port']))
    bottle.run(app=wsgiapp,
               server=config['librarian.server'],
               quiet=config['librarian.log'] != 'yes',
               host=config['librarian.bind'],
               reloader=config['librarian.reloader'] == 'yes',
               port=int(config['librarian.port']))


def configure_argparse(parser):
    parser.add_argument('--conf', metavar='PATH', help='path to configuration '
                        'file', default=CONFPATH)
    parser.add_argument('--debug-conf', action='store_true', help='print out '
                        'the configuration in use and exit')
    parser.add_argument('--version', action='store_true', help='print out '
                        'version number and exit')
    parser.add_argument('--log', metavar='PATH', help='path to log file '
                        '(default: as configured in .ini file)', default=None)
    parser.add_argument('--profile', action='store_true', help='instrument '
                        'the application to perform profiling (default: '
                        'disabled)', default=False)
    parser.add_argument('--su', action='store_true',
                        help='create superuser and exit')


def setup_database(conf):
    app.config.load_config(conf)
    # Run database migrations
    conn = squery.Database.connect(app.config['database.path'])
    db = squery.Database(conn)
    migrations.migrate(db, in_pkg('migrations'), 'librarian.migrations',
                       app.config)
    logging.debug("Finished running migrations")
    bottle.request.db = db


def create_superuser():
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
                         is_superuser=True)
        print("User created.")
    except auth.UserAlreadyExists:
        print("User already exists, please try a different username.")
        create_superuser()
    except auth.InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser()

    sys.exit(0)


def main(conf, debug=False, logpath=None, profile=False):
    app.config.load_config(conf)

    if debug:
        print('Configuration file path: %s' % conf)
        pprint.pprint(app.config, indent=4)
        sys.exit(0)

    start(logpath, profile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    configure_argparse(parser)
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        print('v%s' % __version__)
        sys.exit(0)

    if args.su:
        setup_database(args.conf)
        create_superuser()

    main(args.conf, args.debug_conf, args.log, args.profile)
