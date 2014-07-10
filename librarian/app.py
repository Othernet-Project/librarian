"""
app.py: main web UI module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat
from warnings import warn
from os.path import join, dirname, abspath, normpath

import bottle
from bottle import request, view

import librarian.helpers
from librarian import migrations
from librarian.exceptions import *
from librarian import content_crypto
from librarian import downloads
from librarian import squery
from librarian import send_file
from librarian.i18n import lazy_gettext, I18NPlugin, i18n_path
import librarian

__version__ = librarian.__version__
__autho__ = librarian.__author__


_ = lazy_gettext

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

app = bottle.Bottle()


@app.get('/')
@view('dashboard')
def dashboard():
    """ Render the dashboard """
    spool, content, total = downloads.free_space()
    return locals()


@app.get('/downloads/')
@view('downloads', vals={})
def list_downloads():
    """ Render a list of downloaded content """
    # FIXME: The whole process of decrypting signed content is vulnerable to
    # injection of supposedly decrypted zip files. If attacker is able to gain
    # access to filesystem and is able to write a new zip file in the spool
    # directory, the system will treat it as a safe content file. There are
    # currently no mechanisms for invalidating such files.
    decryptables = downloads.get_decryptable()
    extracted, errors = downloads.decrypt_all(decryptables)
    zipballs = downloads.get_zipballs()
    metadata = []
    for z in zipballs:
        meta = downloads.get_metadata(z)
        meta['md5'] = downloads.get_md5_from_path(z)
        metadata.append(meta)
    # FIXME: Log errors
    return dict(metadata=metadata, errors=errors)


@app.post('/downloads/')
@view('downloads_error')  # TODO: Add this view
def manage_downloads():
    """ Manage the downloaded content """
    forms = request.forms
    action = forms.get('action')
    file_list = forms.getall('selection')
    if not action:
        # Bad action
        return {'error': _('Invalid action, please use one of the form '
                           'buttons.')}
    if action == 'add':
        downloads.add_to_archive(file_list)
    if action == 'delete':
        downloads.remove_downloads(file_list)
    bottle.redirect(i18n_path('/downloads/'))


@app.get('/content/')
@view('content_list')
def content_list():
    """ Show list of content """
    db = request.db
    db.query('SELECT * FROM zipballs ORDER BY updated DESC;')
    return {'metadata': db.cursor.fetchall()}


@app.get('/content/<content_id>/<filename>')
def content_file(content_id, filename):
    zippath = downloads.get_zip_path(content_id)
    try:
        metadata, content = downloads.get_file(zippath, filename)
    except KeyError:
        bottle.abort(404, 'Not found')
    size = metadata.file_size
    timestamp = os.stat(zippath)[stat.ST_MTIME]
    if filename.endswith('.html'):
        # Patch HTML with link to stylesheet
        size, content = downloads.patch_html(content)
    return send_file.send_file(content, filename, size, timestamp)


@app.get('/content/<content_id>/')
def content_index(content_id):
    return content_file(content_id, 'index.html')


@app.get('/static/<path:path>', no_i18n=True)
def send_static(path):
    return bottle.static_file(path, root=STATICDIR)


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
        'h': librarian.helpers,
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
