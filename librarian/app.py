"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
from os.path import join, dirname, abspath, normpath, exists

import bottle
from bottle import request, view

from librarian.i18n import (lazy_gettext as gettext, lazy_ngettext as ngettext,
                            i18n_path, I18NPlugin)
import librarian.helpers
from librarian import migrations
import librarian
__version__ = librarian.__version__
__autho__ = librarian.__author__


_ = gettext

MODDIR = dirname(abspath(__file__))
CONFPATH = normpath(join(MODDIR, '../conf/librarian.ini'))

LANGS = [
    ('de_DE', 'Deutsch'),
    ('en_US', 'English'),
    ('fr_FR', 'français'),
    ('es_ES', 'español'),
    ('zh_CN', '中文')
]
DEFAULT_LOCALE = 'en_US'

app = bottle.Bottle()


@app.get('/')
@view('dashboard')
def dashboard():
    """ Render the dashboard """
    return {}


def start():
    """ Start the application """

    config = app.config

    # Run database migrations
    migrations.connect(config['database.path'])
    migrations.migrate(config['database.migrations'])
    migrations.disconnect()

    # Set some basic configuration
    bottle.TEMPLATE_PATH.insert(0, config['librarian.views'])
    bottle.BaseTemplate.defaults.update({
        'app_version': __version__,
        'request': request,
        'title': _('Librarian'),
        'style': 'site',  # Default stylesheet
        'h': librarian.helpers,
    })

    # Add middlewares
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
    wsgiapp = I18NPlugin(wsgiapp, LANGS, DEFAULT_LOCALE, domain='librarian',
                         locale_dir=config['librarian.locale'])

    # Srart the server
    bottle.run(app=wsgiapp,
               server=config['librarian.server'],
               host=config['librarian.bind'],
               port=config['librarian.port'],
               reloader=config['librarian.debug'],
               debug=config['librarian.debug'])


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
