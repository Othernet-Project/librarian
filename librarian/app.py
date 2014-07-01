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
from bottle import request

import librarian
__version__ = librarian.__version__
__autho__ = librarian.__author__


MODDIR = dirname(abspath(__file__))
CONFPATH = normpath(join(MODDIR, '../conf/librarian.ini'))


app = bottle.Bottle()


@app.get('/')
@bottle.view('dashboard')
def dashboard():
    """ Render the dashboard """
    return {}


def start():
    """ Start the application """

    config = app.config
    bottle.TEMPLATE_PATH.insert(0, config['librarian.views'])
    bottle.BaseTemplate.defaults.update({
        'app_version': __version__,
        'title': config['librarian.default_title'],
        'style': 'site',  # Default stylesheet
    })
    wsgiapp = app  # Pass this variable to WSGI middlewares instead of ``app``
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
    args = parser.parse_args(sys.argv[1:])
    app.config.load_config(args.conf)

    if args.debug_conf:
        pprint.pprint(app.config, indent=4)
        sys.exit(0)

    start()
