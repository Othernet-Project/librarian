"""
downloads.py: routes related to downloads

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
from datetime import datetime

from bottle import request, mako_view as view, redirect
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from ..core import metadata
from ..core import downloads
from ..core import zipballs
from ..lib.pager import Pager
from ..utils.cache import cached
from ..utils.core_helpers import open_archive


validate_zipball = cached()(zipballs.validate)

PER_PAGE = 20


@view('downloads', vals={})
def list_downloads():
    """ Render a list of downloaded content """
    conf = request.app.config
    selection = request.params.get('sel', '0') == '1'

    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang

    zballs = downloads.get_downloads(conf['content.spooldir'],
                                     conf['content.output_ext'])
    zballs = list(reversed(downloads.order_downloads(zballs)))
    if zballs:
        last_zip = datetime.fromtimestamp(zballs[0][1])
        nzipballs = len(zballs)
        logging.info('Found %s updates', nzipballs)
    else:
        last_zip = None
        nzipballs = 0
        logging.info('No updates found')
    # Collect metadata of valid zipballs. If a language filter is specified
    # filter the list based on that.
    metas = []
    for zipball_path, timestamp in zballs:
        logging.debug("Reading zipball: {0}".format(zipball_path))
        try:
            meta = validate_zipball(zipball_path,
                                    meta_filename=conf['content.metadata'])
        except zipballs.ValidationError as exc:
            # Zip file is invalid. This means that the file is corrupted or the
            # original file was signed with corrupt data in it. Either way, we
            # don't know what to do with the file so we'll remove it.
            logging.error("Error reading: {0}: {1}".format(zipball_path, exc))
            downloads.safe_remove(zipball_path)
        else:
            if lang and meta['language'] != lang:
                continue

            meta['md5'] = zipballs.get_md5_from_path(zipball_path)
            meta['ftimestamp'] = datetime.fromtimestamp(timestamp)
            metas.append(metadata.Meta(meta, zipball_path))

    pager = Pager(metas, pid='downloads')
    pager.get_paging_params()
    metas_on_page = pager.get_items()

    archive = open_archive()
    archive.add_replacement_data(metas_on_page, needed_keys=('title',))

    vals = dict(request.params)
    vals.update({'pp': pager.per_page})

    return dict(vals=vals,
                metadata=metas_on_page,
                selection=selection,
                lang=dict(lang=lang),
                pager=pager,
                nzipballs=nzipballs,
                last_zip=last_zip)


@view('downloads_error')  # TODO: Add this view
def manage_downloads():
    """ Manage the downloaded content """
    forms = request.forms
    action = forms.get('action')
    file_list = forms.getall('selection')
    conf = request.app.config
    if not action:
        # Translators, used as error message shown to user when wrong action
        # code is submitted to server
        return {'error': _('Invalid action, please use one of the form '
                           'buttons.')}
    if action == 'add':
        archive = open_archive()
        archive.add_to_archive(file_list)
    if action == 'delete':
        downloads.remove_downloads(conf['content.spooldir'],
                                   md5s=file_list)
    if action == 'deleteall':
        downloads.remove_downloads(conf['content.spooldir'],
                                   extension=conf['content.output_ext'])
    redirect(i18n_url('downloads:list'))
