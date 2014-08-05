"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from warnings import warn
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request

from librarian.exceptions import *
from librarian.lib import content_crypto
from librarian.lib import squery
from librarian.lib.i18n import lazy_gettext as _, I18NPlugin
from librarian.utils import helpers
from librarian.utils import migrations
from librarian.routes import *  # Only importing so routes are rgistered
import librarian

__version__ = librarian.__version__
__author__ = librarian.__author__


MODDIR = dirname(abspath(__file__))
CONFPATH = normpath(join(MODDIR, '../conf/librarian.ini'))
STATICDIR = normpath(join(MODDIR, '../static'))

LANGS = [
    ('de_DE', 'Deutsch'),
    ('en_US', 'English'),
    ('fr_FR', 'français'),
    ('es_ES', 'español'),
    ('zh_CN', '中文')
]
DEFAULT_LOCALE = 'en_US'


app = bottle.default_app()


@app.get('/static/<path:path>', no_i18n=True)
def send_static(path):
    return bottle.static_file(path, root=STATICDIR)


# Note that all other routes are reigsted when ``librarian.routes.*`` is
# imported at the top of this module. All routes are registered against the
# default_app, so they don't need to be mounted explicitly.


def start():
    """ Start the application """

    config = app.config

    # Import gnupg keys
    try:
        content_crypto.import_key(keypath=config['content.key'],
                                  keyring=config['content.keyring'])
    except content_crypto.KeyImportError as err:
        warn(AppStartupWarning(err))

    # Run database migrations
    db = squery.Database(config['database.path'])
    migrations.migrate(db, config['database.migrations'])
    db.disconnect()

    app.install(squery.database_plugin)

    # Set some basic configuration
    bottle.TEMPLATE_PATH.insert(0, config['librarian.views'])
    bottle.BaseTemplate.defaults.update({
        'app_version': __version__,
        'request': request,
        'title': _('Librarian'),
        'style': 'screen',  # Default stylesheet
        'h': helpers,
    })

    # Add middlewares
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
    wsgiapp = I18NPlugin(wsgiapp, langs=LANGS, default_locale=DEFAULT_LOCALE,
                         domain='librarian',
                         locale_dir=config['librarian.locale'])

    # Srart the server
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
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        print('v%s' % __version__)
        sys.exit(0)

    app.config.load_config(args.conf)

    if args.debug_conf:
        pprint.pprint(app.config, indent=4)
        sys.exit(0)

    start()
