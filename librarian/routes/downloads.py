"""
downloads.py: routes related to downloads

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.i18n import lazy_ngettext, lazy_gettext as _, i18n_url

from ..core import downloads
from ..lib.auth import login_required
from ..lib.paginator import Paginator
from ..utils.cache import invalidates
from ..utils.core_helpers import open_archive, filter_downloads
from ..utils.template import view


@login_required()
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


def notify_content_added(content_id_list, chunk_size=100):
    archive = open_archive()
    id_list = (content_id_list[i:i + chunk_size]
               for i in range(0, len(content_id_list), chunk_size))
    for content_ids in id_list:
        content_list = archive.get_multiple(content_ids,
                                            fields=('md5', 'title'))
        for content_item in content_list:
            content_data = {'id': content_item['md5'],
                            'title': content_item['title']}
            request.app.exts.notifications.send(content_data,
                                                category='content')


@invalidates(prefix=['content', 'downloads'], after=True)
def add(file_list):
    archive = open_archive()
    added_count = archive.add_to_archive(file_list)
    notify_content_added(file_list)
    # Translators, used as confirmation title after the chosen updates were
    # successfully added to the library
    title = _("Updates added")
    # Translators, used as confirmation message after the chosen updates were
    # successfully added to the library
    message = lazy_ngettext(
        "An update has been added to the Library.",
        "{update_count} updates have been added to the Library.",
        added_count
    ).format(update_count=added_count)
    return dict(page_title=title,
                message=message,
                redirect_url=i18n_url('downloads:list'),
                redirect_target=_("Updates"))


@invalidates(prefix=['content', 'downloads'], after=True)
def add_all(*args):
    all_files = [meta['md5'] for meta in filter_downloads(lang=None)]
    archive = open_archive()
    added_count = archive.add_to_archive(all_files)
    notify_content_added(all_files)
    # Translators, used as confirmation title after the chosen updates were
    # successfully added to the library
    title = _("Updates added")
    # Translators, used as confirmation message after the chosen updates were
    # successfully added to the library
    message = lazy_ngettext(
        "An update has been added to the Library.",
        "{update_count} updates have been added to the Library.",
        added_count
    ).format(update_count=added_count)
    return dict(page_title=title,
                message=message,
                redirect_url=i18n_url('downloads:list'),
                redirect_target=_("Updates"))


@invalidates(prefix=['downloads'], after=True)
def delete(file_list):
    spooldir = request.app.config['content.spooldir']
    removed_count = downloads.remove_downloads(spooldir, content_ids=file_list)
    # Translators, used as confirmation title after the chosen updates were
    # deleted on the updates page
    title = _("Updates deleted")
    # Translators, used as confirmation message after the chosen updates were
    # deleted on the updates page
    message = lazy_ngettext("An update has been deleted.",
                            "{update_count} updates have been deleted.",
                            removed_count).format(update_count=removed_count)
    return dict(page_title=title,
                message=message,
                redirect_url=i18n_url('downloads:list'),
                redirect_target=_("Updates"))


@invalidates(prefix=['downloads'], after=True)
def delete_all(*args):
    spooldir = request.app.config['content.spooldir']
    content_ext = request.app.config['content.output_ext']
    removed_count = downloads.remove_downloads(spooldir, extension=content_ext)
    # Translators, used as confirmation title after the chosen updates were
    # deleted on the updates page
    title = _("Updates deleted")
    # Translators, used as confirmation message after the chosen updates were
    # deleted on the updates page
    message = lazy_ngettext("An update has been deleted.",
                            "{update_count} updates have been deleted.",
                            removed_count).format(update_count=removed_count)
    return dict(page_title=title,
                message=message,
                redirect_url=i18n_url('downloads:list'),
                redirect_target=_("Updates"))


@login_required()
@view('feedback')
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
        feedback = dict(page_title=title,
                        message=message,
                        redirect_url=i18n_url('downloads:list'),
                        redirect_target=_("Updates"))
    else:
        status = 'success'
        feedback = handler(file_list)

    return dict(status=status, **feedback)


def routes(app):
    return (
        ('downloads:list', list_downloads, 'GET', '/downloads/', {}),
        ('downloads:action', manage_downloads, 'POST', '/downloads/', {}),
    )
