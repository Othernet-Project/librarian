"""
downloads.py: routes related to downloads

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ..core import downloads
from ..lib.paginator import Paginator
from ..utils.core_helpers import open_archive, filter_downloads
from ..utils.template import template, view


@view('downloads')
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
    metas = filter_downloads(lang)
    # paginate query results
    paginator = Paginator(metas, page, per_page)
    # request params need to be returned as well
    vals = dict(request.params)
    vals.update({'pp': per_page, 'p': page})
    return dict(vals=vals,
                nzipballs=len(metas),
                last_zball=metas[0]['ftimestamp'] if metas else None,
                pager=paginator,
                selection=selection,
                lang=dict(lang=lang),
                metadata=paginator.items)


def add(file_list):
    archive = open_archive()
    added_count = archive.add_to_archive(file_list)
    request.app.exts.cache.invalidate(prefix='content')
    request.app.exts.cache.invalidate(prefix='downloads')
    request.app.exts.notifications.send(_('Content added.'),
                                        category='content')
    # Translators, used as confirmation title after the chosen updates were
    # successfully added to the library
    title = _("Updates added")
    # Translators, used as confirmation message after the chosen updates were
    # successfully added to the library
    message = _("{update_count} update(s) have been added to the Library.")
    message = message.format(update_count=added_count)
    url = i18n_url('content:list')
    return (title, message, url)


def add_all(*args):
    all_files = [meta['md5'] for meta in filter_downloads(lang=None)]
    archive = open_archive()
    added_count = archive.add_to_archive(all_files)
    request.app.exts.cache.invalidate(prefix='content')
    request.app.exts.cache.invalidate(prefix='downloads')
    request.app.exts.notifications.send(_('Content added.'),
                                        category='content')
    # Translators, used as confirmation title after the chosen updates were
    # successfully added to the library
    title = _("Updates added")
    # Translators, used as confirmation message after the chosen updates were
    # successfully added to the library
    message = _("{update_count} update(s) have been added to the Library.")
    message = message.format(update_count=added_count)
    url = i18n_url('content:list')
    return (title, message, url)


def delete(file_list):
    spooldir = request.app.config['content.spooldir']
    removed_count = downloads.remove_downloads(spooldir, content_ids=file_list)
    request.app.exts.cache.invalidate(prefix='downloads')
    # Translators, used as confirmation title after the chosen updates were
    # deleted on the updates page
    title = _("Updates deleted")
    # Translators, used as confirmation message after the chosen updates were
    # deleted on the updates page
    message = _("{update_count} update(s) have been deleted.")
    message = message.format(update_count=removed_count)
    # if no updates remained, redirect to content page
    updates = filter_downloads(lang=None)
    url = i18n_url('downloads:list') if updates else i18n_url('content:list')
    return (title, message, url)


def delete_all(*args):
    spooldir = request.app.config['content.spooldir']
    content_ext = request.app.config['content.output_ext']
    removed_count = downloads.remove_downloads(spooldir, extension=content_ext)
    request.app.exts.cache.invalidate(prefix='downloads')
    # Translators, used as confirmation title after the chosen updates were
    # deleted on the updates page
    title = _("Updates deleted")
    # Translators, used as confirmation message after the chosen updates were
    # deleted on the updates page
    message = _("{update_count} update(s) have been deleted.")
    message = message.format(update_count=removed_count)
    url = i18n_url('content:list')
    return (title, message, url)


def manage_downloads():
    """ Manage the downloaded content """
    action_handlers = {'add': add,
                       'add_all': add_all,
                       'delete': delete,
                       'delete_all': delete_all}
    action = request.forms.get('action')
    file_list = request.forms.getall('selection')
    try:
        handler = action_handlers[action]
    except KeyError:
        # Translators, used as error title shown to user when wrong action
        # code is submitted to server
        title = _("Invalid action")
        # Translators, used as error message shown to user when wrong action
        # code is submitted to server
        message = _('Invalid action, please use one of the form buttons.')
        status = 'error'
    else:
        (title, message, url) = handler(file_list)
        status = 'success'

    return template('feedback',
                    status=status,
                    page_title=title,
                    message=message,
                    redirect=url)
