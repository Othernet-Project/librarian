"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
from warnings import warn
from logging.config import dictConfig as log_config
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request

from librarian.exceptions import *
from librarian.lib import content_crypto
from librarian.lib import squery
from librarian.lib.i18n import lazy_gettext as _, I18NPlugin
from librarian.lib import html as helpers
from librarian.lib.lazy import Lazy
from librarian.lib.downloads import get_zipballs
from librarian.utils import migrations
from librarian.routes import *  # Only importing so routes are rgistered
import librarian

__version__ = librarian.__version__
__author__ = librarian.__author__


MODDIR = dirname(abspath(__file__))

def in_pkg(*paths):
    """ Return path relative to module directory """
    return normpath(join(MODDIR, *paths))

CONFPATH = in_pkg('librarian.ini')
STATICDIR = in_pkg('static')

LANGS = [
    ('en_US', 'English'),
]
DEFAULT_LOCALE = 'en_US'


app = bottle.default_app()


@app.get('/static/<path:path>', no_i18n=True)
def send_static(path):
    return bottle.static_file(path, root=STATICDIR)


# Note that all other routes are reigsted when ``librarian.routes.*`` is
# imported at the top of this module. All routes are registered against the
# default_app, so they don't need to be mounted explicitly.


def start(logfile=None):
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

    # Import gnupg keys
    try:
        content_crypto.import_key(in_pkg('keys', config['content.key']),
                                  keyring=config['content.keyring'])
    except content_crypto.KeyImportError as err:
        logging.error("Could not import keys: %s" % err)
        warn(AppStartupWarning(err))

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
    })

    # Add middlewares
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
    wsgiapp = I18NPlugin(wsgiapp, langs=LANGS, default_locale=DEFAULT_LOCALE,
                         domain='librarian', locale_dir=in_pkg('locales'))

    # Srart the server
    logging.info('Starting Librarian')
    bottle.run(app=wsgiapp,
               server=config['librarian.server'],
               host=config['librarian.bind'],
               port=int(config['librarian.port']),
               reloader=config['librarian.debug'] == 'yes',
               debug=config['librarian.debug'] == 'yes')


if __name__ == '__main__':
    import sys
    import pprint
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', metavar='PATH', help='path to configuration '
                        'file', default=CONFPATH)
    parser.add_argument('--debug-conf', action='store_true', help='print out '
                        'the configuration in use and exit')
    parser.add_argument('--version', action='store_true', help='print out '
                        'version number and exit')
    parser.add_argument('--log', metavar='PATH', help='path to log file '
                        '(default: as configured in .ini file)', default=None)
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        print('v%s' % __version__)
        sys.exit(0)

    app.config.load_config(args.conf)

    if args.debug_conf:
        pprint.pprint(app.config, indent=4)
        sys.exit(0)

    start(args.log)
