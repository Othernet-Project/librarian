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
gevent.monkey.patch_all(aggressive=True, thread=False)

# For more details on the below see: http://bit.ly/18fP1uo
import gevent.hub
gevent.hub.Hub.NOT_ERROR = (Exception,)

import sys
import time
import pprint
import logging
from logging.config import dictConfig as log_config
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request

from bottle_utils.lazy import Lazy
from bottle_utils import html as helpers
from bottle_utils.i18n import I18NPlugin, lazy_gettext as _
from bottle_utils.common import to_unicode

from librarian.core.metadata import LICENSES
from librarian.core.downloads import get_zipballs

from librarian.lib import auth
from librarian.lib import setup
from librarian.lib import sessions
from librarian.lib import squery
from librarian.lib.lock import lock_plugin
from librarian.lib.confloader import ConfDict

from librarian.utils import lang
from librarian.utils import commands
from librarian.utils import migrations
from librarian.utils.repl import start_repl
from librarian.utils.system import ensure_dir
from librarian.utils.routing import add_routes
from librarian.utils.timer import request_timer
from librarian.utils.gserver import ServerManager
from librarian.utils import databases as database_utils
from librarian.utils.signal_handlers import on_interrupt
from librarian.utils.template_helpers import template_helper
from librarian.utils.content_domain_handler import content_resolver_plugin

from librarian.plugins import install_plugins

from librarian.routes import (content, tags, downloads, apps, dashboard,
                              system, auth as auth_route, setup as setup_route)

from librarian import __version__

MODDIR = dirname(abspath(__file__))
APP_ONLY_PLUGINS = ('session', 'user', 'setup')


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

    ('auth:login_form', auth_route.show_login_form,
     'GET', '/login/', {}),
    ('auth:login', auth_route.login,
     'POST', '/login/', {}),
    ('auth:logout', auth_route.logout,
     'GET', '/logout/', {}),

    # Content

    ('content:list', content.content_list,
     'GET', '/', {}),
    ('content:sites_list', content.content_sites_list,
     'GET', '/sites', {}),
    ('content:file', content.content_file,
     'GET', '/pages/<content_id>/<filename:path>',
     dict(no_i18n=True, skip=APP_ONLY_PLUGINS)),
    ('content:zipball', content.content_zipball,
     'GET', '/pages/<content_id>.zip',
     dict(no_i18n=True, unlocked=True, skip=APP_ONLY_PLUGINS)),
    ('content:reader', content.content_reader,
     'GET', '/pages/<content_id>', {}),
    ('content:cover', content.cover_image,
     'GET', '/covers/<path>', dict(no_i18n=True, skip=APP_ONLY_PLUGINS)),
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

    # Setup wizard

    ('setup:main', setup.setup_wizard,
     ['GET', 'POST'], '/setup/', {}),

    # Apps

    ('apps:list', apps.show_apps,
     'GET', '/apps/', dict(unlocked=True)),
    ('apps:app', apps.send_app_file,
     'GET', '/apps/<appid>/', dict(unlocked=True)),
    ('apps:asset', apps.send_app_file,
     'GET', '/apps/<appid>/<path:path>', dict(unlocked=True)),

    # System

    ('sys:static', system.send_static,
     'GET', '/static/<path:path>',
     dict(no_i18n=True, unlocked=True, skip=APP_ONLY_PLUGINS)),
    ('sys:favicon', system.send_favicon,
     'GET', '/favicon.ico',
     dict(no_i18n=True, unlocked=True, skip=APP_ONLY_PLUGINS)),
    ('sys:logs', system.send_logfile,
     'GET', '/librarian.log',
     dict(no_i18n=True, unlocked=True, skip=APP_ONLY_PLUGINS)),

    # This route handler is added because unhandled missing pages cause bottle
    # to _not_ install any plugins, and some are essential to rendering of the
    # 404 page (e.g., i18n, sessions, auth).
    ('sys:all404', system.all_404,
     ['GET', 'POST'], '/<path:path>', dict()),
)

app = bottle.default_app()
# register session secret auto configurator
setup.autoconfigurator('session.secret')(sessions.generate_secret_key)


def prestart(config, logfile=None, debug=False):
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
                'maxBytes': config['logging.size'],
                'backupCount': config['logging.backups'],
            },
        },
        'formatters': {
            'default': {
                'format': config['logging.format'],
                'datefmt': config['logging.date_format'],
            },
        },
    })
    debug = debug or config['librarian.debug']
    logging.info('Configuring Librarian environment')

    database_configs = database_utils.get_database_configs(config)
    for db_name, db_path in database_configs.items():
        logging.debug('Using database {}'.format(db_path))

    # Make sure all necessary directories are present
    ensure_dir(dirname(config['logging.output']))
    for db_path in database_configs.values():
        ensure_dir(dirname(db_path))

    ensure_dir(config['content.spooldir'])
    ensure_dir(config['content.appdir'])
    ensure_dir(config['content.contentdir'])
    ensure_dir(config['content.covers'])

    # Run database migrations
    databases = squery.get_databases(database_configs, debug=debug)
    for db_name, db in databases.items():
        migrations.migrate(db,
                           in_pkg('migrations', db_name),
                           'librarian.migrations.{0}'.format(db_name),
                           config)

    logging.debug("Finished running migrations")
    return databases


def start(databases, config, no_auth=False, repl=False, debug=False):
    """ Start the application """

    debug = debug or config['librarian.debug']

    servers = ServerManager()

    # Srart the server
    logging.info('===== Starting Librarian v%s =====', __version__)

    # Install Librarian plugins
    install_plugins(app)
    logging.info('Installed all plugins')

    # Set some basic configuration
    # add `lang_name_safe` to template helpers
    template_helper(lang.lang_name_safe)
    bottle.TEMPLATE_PATH.insert(0, in_pkg('views'))
    bottle.BaseTemplate.defaults.update({
        'app_version': __version__,
        'request': request,
        'style': 'screen',  # Default stylesheet
        'h': helpers,
        'th': template_helper,
        'updates': Lazy(lambda: len(list(get_zipballs(
            config['content.spooldir'],
            config['content.output_ext']
        )))),
        'readable_license': lambda s: _(dict(LICENSES).get(s, LICENSES[0][1])),
        'is_rtl': Lazy(lambda: request.locale in lang.RTL_LANGS),
        'dir': lambda l: 'rtl' if l in lang.RTL_LANGS else 'auto',
        'LANGS': lang.LANGS,
        'UI_LANGS': lang.UI_LANGS,
        'SELECT_LANGS': lang.SELECT_LANGS,
        'u': to_unicode,
        'url': app.get_url,
    })

    # Install bottle plugins and WSGI middleware
    app.install(request_timer('Total'))
    app.install(squery.database_plugin(databases, debug=debug and not repl))
    app.install(sessions.session_plugin(
        cookie_name=config['session.cookie_name'],
        secret=app.setup.get('session.secret')
    ))
    app.install(auth.user_plugin(no_auth))
    wsgiapp = I18NPlugin(app, langs=lang.UI_LANGS,
                         default_locale=lang.DEFAULT_LOCALE,
                         domain='librarian', locale_dir=in_pkg('locales'))
    app.install(lock_plugin)
    app.install(setup.setup_plugin(config['setup.base_template'],
                                   config['setup.finished_template']))
    app.install(content_resolver_plugin(
        root_url=config['librarian.root_url'],
        ap_client_ip_range=config['librarian.ap_client_ip_range']
    ))
    app.install(request_timer('Handler'))

    # Install routes
    add_routes(app, ROUTES)
    app.error(403)(system.show_access_denied_page)
    app.error(404)(system.show_page_missing)
    app.error(500)(system.show_error_page)
    app.error(503)(system.show_maint_page)

    # Prepare to start
    bottle.debug(debug)

    # We are passing the ``wsgiapp`` object here because that's the one that
    # contains the I18N middleware. If we pass ``app`` object, then we won't
    # have the I18N middleware active at all.
    servers.start_server('librarian', config, wsgiapp)

    if repl:
        repl_thread = start_repl(
            locals(), 'Press Ctrl-C to shut down Librarian.')
    else:
        repl_thread = None
        print('Press Ctrl-C to shut down Librarian.')

    def shutdown(*args, **kwargs):
        """ Cleanly shut down the server """
        logging.info('Librarian is going down.')
        if repl_thread:
            repl_thread.join()
        servers.stop_all(5)
        for db in databases.values():
            db.close()
        logging.info('Clean shutdown completed')
        print('Bye! Have a nice day! Those books are due Tuesday, by the way!')

    on_interrupt(shutdown)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt received')
    return shutdown()


def configure_argparse(parser):
    parser.add_argument('--conf', metavar='PATH', help='path to configuration '
                        'file', default=CONFPATH)
    parser.add_argument('--debug-conf', action='store_true', help='print out '
                        'the configuration in use and exit')
    parser.add_argument('--debug', action='store_true', help='enable '
                        'debugging')
    parser.add_argument('--version', action='store_true', help='print out '
                        'version number and exit')
    parser.add_argument('--log', metavar='PATH', help='path to log file '
                        '(default: as configured in .ini file)', default=None)
    parser.add_argument('--no-auth', action='store_true',
                        help='disable authentication')
    parser.add_argument('--repl', action='store_true',
                        help='start interactive shell after servers start')
    commands.add_command_switches(parser)


def main(args):
    app.config = ConfDict.from_file(args.conf, catchall=True, autojson=True)
    conf = app.config
    app.setup = setup.Setup(conf['setup.file'])

    if args.debug_conf:
        print('Configuration file path: %s' % args.conf)
        pprint.pprint(app.config, indent=4)
        sys.exit(0)

    databases = prestart(conf, args.log, args.debug)
    commands.select_command(args, databases, app)
    return start(databases, conf, args.no_auth, args.repl, args.debug)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    configure_argparse(parser)
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        print('v%s' % __version__)
        sys.exit()

    sys.exit(main(args))
