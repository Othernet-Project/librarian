# -*- coding: utf-8 -*-

"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals, print_function

import sys
import pprint
import logging
from warnings import warn
from logging.config import dictConfig as log_config
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request

from exceptions import *
from lib import squery
from lib.i18n import lazy_gettext as _, I18NPlugin
from lib import html as helpers
from lib.lazy import Lazy
from lib.downloads import get_zipballs
from lib.archive import LICENSES
from lib.common import to_unicode
from lib.system import ensure_dir
from utils import migrations
from routes import (content, tags, downloads, apps, dashboard)

from . import __version__, __author__

MODDIR = dirname(abspath(__file__))

def in_pkg(*paths):
    """ Return path relative to module directory """
    return normpath(join(MODDIR, *paths))

CONFPATH = in_pkg('librarian.ini')
STATICDIR = in_pkg('static')

LOCALES = [
    ('ar', 'اللغة العربية'),
    ('da', 'Dansk'),
    ('de', 'Deutsch'),
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('hi', 'हिन्दी'),
    ('it', 'Italiano'),
    ('jp', '日本語'),
    ('nb', 'Norsk'),
    ('nl', 'Nederlands'),
    ('pt', 'Português'),
    ('ru', 'Русский'),
    ('sr', 'Srpski'),
    ('sv', 'Svensk'),
    ('ta', 'தமிழ்'),
    ('tr', 'Türkçe'),
    ('zh', '中文'),
]
RTL_LANGS = ['ar', 'he', 'ur', 'yi', 'ji', 'iw', 'fa']
DEFAULT_LOCALE = 'en'


app = bottle.default_app()

# Content
app.route('/', 'GET',
          callback=content.content_list)
app.route('/pages/<content_id>/<filename:path>', 'GET', skip=['i18n'],
          callback=content.content_file)
app.route('/pages/<content_id>', 'GET',
          callback=content.content_reader)
app.route('/covers/<path:path>', 'GET',
          callback=content.cover_image, skip=['i18n'])
app.route('/delete/<content_id>', 'POST',
          callback=content.remove_content)

# Files
app.route('/files/', 'GET',
          callback=content.show_file_list)
app.route('/files/<path:path>', 'GET',
          callback=content.show_file_list)
app.route('/files/<path:path>', 'POST',
          callback=content.handle_file_action)

# Tags
app.route('/tags/', 'GET',
          callback=tags.tag_cloud)
app.route('/tags/<content_id>', 'POST',
          callback=tags.edit_tags)

# Updates
app.route('/downloads/', 'GET',
          callback=downloads.list_downloads)
app.route('/downloads/', 'POST',
          callback=downloads.manage_downloads)

# Dashboard
app.route('/dashboard/', 'GET',
          callback=dashboard.dashboard)
app.route('/dashboard/cleanup/', 'GET',
          callback=dashboard.cleanup_list)
app.route('/dashboard/cleanup/', 'POST',
          callback=dashboard.cleanup)

# Apps
app.route('/apps/', 'GET',
          callback=apps.show_apps)
app.route('/apps/<appid>/', 'GET',
          callback=apps.send_app_file)
app.route('/apps/<appid>/<path:path>', 'GET',
          callback=apps.send_app_file)


@app.get('/static/<path:path>', skip=['i18n'])
def send_static(path):
    return bottle.static_file(path, root=STATICDIR)


# Note that all other routes are reigsted when ``librarian.routes.*`` is
# imported at the top of this module. All routes are registered against the
# default_app, so they don't need to be mounted explicitly.


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
                'class' : 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': logfile or config['logging.output'],
                'maxBytes': int(config['logging.size']),
                'backupCount': int(config['logging.backups'])
            },
        },
        'formatters': {
            'default': {
                'format' : config['logging.format'],
                'datefmt' : config['logging.date_format']
            },
        },
    })

    # Make sure all necessary directories are present
    ensure_dir(dirname(config['logging.output']))
    ensure_dir(dirname(config['database.path']))
    ensure_dir(config['content.spooldir'])
    ensure_dir(config['content.appdir'])
    ensure_dir(config['content.contentdir'])
    ensure_dir(config['content.covers'])

    # Run database migrations
    db = squery.Database(config['database.path'])
    migrations.migrate(db, in_pkg('migrations'))
    logging.debug("Finished running migrations")
    db.disconnect()

    app.install(squery.database_plugin)

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
        'is_rtl': Lazy(lambda: request.locale in RTL_LANGS),
        'u': to_unicode,
    })

    # Add middlewares
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
    wsgiapp = I18NPlugin(wsgiapp, langs=LOCALES, default_locale=DEFAULT_LOCALE,
                         domain='librarian', locale_dir=in_pkg('locales'))

    # Srart the server
    logging.info('Starting Librarian')

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
    bottle.run(app=wsgiapp,
               server=config['librarian.server'],
               host=config['librarian.bind'],
               reloader=config['librarian.server'] == 'wsgiref',
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


def main(conf, debug=False, logpath=None, profile=False):
    app.config.load_config(conf)

    if debug:
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

    main(args.conf, args.debug_conf, args.log, args.profile)
