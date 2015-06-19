"""
downloads.py: routes related to downloads

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
from datetime import datetime

from bottle import request, redirect
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from ..core import metadata
from ..core import downloads
from ..core import zipballs
from ..lib.paginator import Paginator
from ..utils.cache import cached
from ..utils.core_helpers import open_archive
from ..utils.template import view


read_meta = cached()(zipballs.validate)


@cached(prefix='downloads', timeout=30)
def get_download_paths():
    paths = downloads.get_downloads(request.app.config['content.spooldir'],
                                    request.app.config['content.output_ext'])
    return list(reversed(downloads.order_downloads(paths)))


@cached(prefix='downloads', timeout=30)
def filter_downloads(lang):
    conf = request.app.config
    zballs = get_download_paths()
    zball_count = len(zballs)
    last_zball = datetime.fromtimestamp(zballs[0][1]) if zballs else None
    logging.info('Found {0} updates'.format(zball_count))
    # Collect metadata of valid zipballs. If a language filter is specified
    # filter the list based on that.
    meta_filename = conf['content.metadata']
    metas = []
    for zipball_path, timestamp in zballs:
        try:
            meta = read_meta(zipball_path, meta_filename=meta_filename)
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

    archive = open_archive()
    archive.add_replacement_data(metas, needed_keys=('title',))

    return dict(metadata=metas,
                nzipballs=zball_count,
                last_zip=last_zball)


@view('downloads', vals={})
def list_downloads():
    """ Render a list of downloaded content """
    selection = request.params.get('sel', '0') == '1'
    # parse language filter
    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang
    # parse pagination params
    page = Paginator.parse_page(request.params)
    per_page = Paginator.parse_per_page(request.params)
    # get downloads filtered by above parsed filter params
    result = filter_downloads(lang)

    paginator = Paginator(result['metadata'], page, per_page)
    vals = dict(request.params)
    vals.update({'pp': per_page, 'p': page})

    result.update(dict(vals=vals,
                       pager=paginator,
                       selection=selection,
                       lang=dict(lang=lang),
                       metadata=paginator.items))
    return result


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
        request.app.exts.cache.invalidate(prefix='content')
        request.app.exts.cache.invalidate(prefix='downloads')
        request.app.exts.notifications.send(_('Content added.'),
                                            category='content')
    if action == 'delete':
        downloads.remove_downloads(conf['content.spooldir'],
                                   content_ids=file_list)
        request.app.exts.cache.invalidate(prefix='downloads')
    if action == 'deleteall':
        downloads.remove_downloads(conf['content.spooldir'],
                                   extension=conf['content.output_ext'])
        request.app.exts.cache.invalidate(prefix='downloads')

    redirect(i18n_url('downloads:list'))


def routes(app):
    return (
        ('downloads:list', list_downloads, 'GET', '/downloads/', {}),
        ('downloads:action', manage_downloads, 'POST', '/downloads/', {}),
    )
