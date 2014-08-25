"""
downloads.py: routes related to downloads

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging

from bottle import request, view, redirect, default_app

from ..lib import archive
from ..lib import downloads
from ..lib.i18n import i18n_path, lazy_gettext as _

__all__ = ('app', 'list_downloads', 'manage_downloads',)

PREFIX = '/downloads'


app = default_app()


@app.get(PREFIX + '/')
@view('downloads', vals={})
def list_downloads():
    """ Render a list of downloaded content """
    # FIXME: The whole process of decrypting signed content is vulnerable to
    # injection of supposedly decrypted zip files. If attacker is able to gain
    # access to filesystem and is able to write a new zip file in the spool
    # directory, the system will treat it as a safe content file. There are
    # currently no mechanisms for invalidating such files.
    decryptables = downloads.get_decryptable()
    logging.debug("Found %s decryptable files" % (len(decryptables)))
    extracted, errors = downloads.decrypt_all(decryptables)
    zipballs = list(downloads.get_zipballs())
    logging.info("Found %s decrypted files" % (len(zipballs)))
    metadata = []
    for z in zipballs:
        logging.debug("<%s> getting metadata" % z)
        try:
            meta = downloads.get_metadata(z)
            meta['md5'] = downloads.get_md5_from_path(z)
            metadata.append(meta)
        except downloads.ContentError as err:
            # Zip file is invalid. This means that the file is corrupted or the
            # original file was signed with corrupt data in it. Either way, we
            # don't know what to do with the file so we'll remove it.
            logging.error("<%s> error unpacking: %s" % (z, err))
            os.unlink(z)
    # FIXME: Log errors
    return dict(metadata=metadata, errors=errors)


@app.post(PREFIX + '/')
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
        archive.add_to_archive(file_list)
    if action == 'delete':
        downloads.remove_downloads(file_list)
    redirect(i18n_path('/downloads/'))

