"""
downloads.py: routes related to downloads

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging
from datetime import datetime

from bottle import request, mako_view as view, redirect
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from ..core import metadata
from ..core import downloads
from ..lib.pager import Pager
from ..utils.cache import cached
from ..utils.core_helpers import open_archive


get_metadata = cached()(downloads.get_metadata)

PER_PAGE = 20


@view('downloads', vals={})
def list_downloads():
    """ Render a list of downloaded content """
    conf = request.app.config
    selection = request.params.get('sel', '0') == '1'

    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang

    zipballs = downloads.get_zipballs(conf['content.spooldir'],
                                      conf['content.output_ext'])
    zipballs = list(reversed(downloads.order_zipballs(zipballs)))
    if zipballs:
        last_zip = datetime.fromtimestamp(zipballs[0][1])
        nzipballs = len(zipballs)
        logging.info('Found %s updates', nzipballs)
    else:
        last_zip = None
        nzipballs = 0
        logging.info('No updates found')
    # Collect metadata of valid zipballs. If a language filter is specified
    # filter the list based on that.
    metas = []
    for z, ts in zipballs:
        logging.debug("<%s> getting metas" % z)
        try:
            meta = get_metadata(z, conf['content.metadata'])
            if lang and meta['language'] != lang:
                continue

            meta['md5'] = downloads.get_md5_from_path(z)
            meta['ftimestamp'] = datetime.fromtimestamp(ts)
            metas.append(metadata.Meta(meta, z))
        except downloads.ContentError as err:
            # Zip file is invalid. This means that the file is corrupted or the
            # original file was signed with corrupt data in it. Either way, we
            # don't know what to do with the file so we'll remove it.
            logging.error("<%s> error unpacking: %s" % (z, err))
            os.unlink(z)
            continue

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
