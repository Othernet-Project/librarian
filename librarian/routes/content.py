"""
content.py: routes related to content

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools
import os

from bottle import request, abort, default_app, static_file
from bottle_utils.ajax import roca_view
from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.i18n import lazy_gettext as _, i18n_url
from fdsend import send_file

from ..core import content
from ..core import metadata
from ..core import zipballs

from ..lib import auth
from ..lib.paginator import Paginator

from ..utils.cache import cached
from ..utils.template import template, view
from ..utils.core_helpers import open_archive, with_content


app = default_app()


@cached(prefix='content', timeout=300)
def filter_content(query, lang, tag, multipage):
    conf = request.app.config
    archive = open_archive()
    raw_metas = archive.get_content(terms=query,
                                    lang=lang,
                                    tag=tag,
                                    multipage=multipage)
    contentdir = conf['content.contentdir']
    metas = [metadata.Meta(meta, content.to_path(meta['md5'], contentdir))
             for meta in raw_metas]
    return metas


def prepare_content_list(multipage=None):
    # parse search query
    query = request.params.getunicode('q', '').strip()
    # parse language filter
    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang
    # parse tag filter
    archive = open_archive()
    try:
        tag = int(request.params.get('tag'))
    except (TypeError, ValueError):
        tag = None
        tag_name = None
    else:
        try:
            tag_name = archive.get_tag_name(tag)['name']
        except (IndexError, KeyError):
            abort(404, _('Specified tag was not found'))
    # parse pagination params
    page = Paginator.parse_page(request.params)
    per_page = Paginator.parse_per_page(request.params)
    # get content list filtered by above parsed filter params
    metas = filter_content(query, lang, tag, multipage)
    pager = Paginator(metas, page, per_page)
    return dict(metadata=pager.items,
                pager=pager,
                vals=request.params.decode(),
                query=query,
                lang=dict(lang=lang),
                tag=tag_name,
                tag_id=tag,
                tag_cloud=archive.get_tag_cloud())


@roca_view('content_list', '_content_list', template_func=template)
def content_list():
    """ Show list of content """
    result = prepare_content_list()
    result.update({'base_path': i18n_url('content:list'),
                   'page_title': _('Library'),
                   'empty_message': _('Content library is currently empty')})
    return result


@roca_view('content_list', '_content_list', template_func=template)
def content_sites_list():
    """ Show list of multipage content only """
    result = prepare_content_list(multipage=True)
    result.update({'base_path': i18n_url('content:sites_list'),
                   'page_title': _('Sites'),
                   'empty_message': _('There are no sites in the library.')})
    return result


def guard_already_removed(func):
    @functools.wraps(func)
    def wrapper(content_id, **kwargs):
        archive = open_archive()
        content = archive.get_single(content_id)
        if not content:
            # Translators, used as page title when a content item's removal is
            # retried, but it was already deleted before
            title = _("Content already removed")
            # Translators, used as message when a content item's removal is
            # retried, but it was already deleted before
            message = _("The specified content has already been removed.")
            return template('feedback',
                            status='success',
                            page_title=title,
                            message=message,
                            redirect_url=i18n_url('content:list'),
                            redirect_target=_("Library"))

        return func(content=content, **kwargs)
    return wrapper


@auth.login_required(next_to='/')
@csrf_token
@guard_already_removed
@view('remove_confirm')
def remove_content_confirm(content):
    cancel_url = request.headers.get('Referer', i18n_url('content:list'))
    return dict(content=content, cancel_url=cancel_url)


@auth.login_required(next_to='/')
@csrf_protect
@guard_already_removed
@view('feedback')
def remove_content(content):
    """ Delete a single piece of content from archive """
    archive = open_archive()
    archive.remove_from_archive([content.md5])
    request.app.exts.cache.invalidate(prefix='content')
    # Translators, used as page title of successful content removal feedback
    page_title = _("Content removed")
    # Translators, used as message of successful content removal feedback
    message = _("Content successfully removed.")
    return dict(status='success',
                page_title=page_title,
                message=message,
                redirect_url=i18n_url('content:list'),
                redirect_target=_("Library"))


def content_file(content_path, filename):
    """ Serve file from content directory with specified id """
    # TODO: handle `keep_formatting` flag
    content_dir = request.app.config['content.contentdir']
    content_root = os.path.join(content_dir, content_path)
    return static_file(filename, root=content_root)


@cached(prefix='zipball')
def prepare_zipball(content_id):
    content_dir = request.app.config['content.contentdir']
    zball = zipballs.create(content_id, content_dir)
    return zball.getvalue()


def content_zipball(content_id):
    """ Serve zipball with specified id """
    zball = zipballs.StringIO(prepare_zipball(content_id))
    filename = '{0}.zip'.format(content_id)
    return send_file(zball, filename, attachment=True)


@view('reader')
@with_content
def content_reader(meta):
    """ Loads the reader interface """
    archive = open_archive()
    archive.add_view(meta.md5)
    file_path = request.params.get('path', meta.entry_point)
    file_path = meta.entry_point if file_path == '/' else file_path
    if file_path.startswith('/'):
        file_path = file_path[1:]

    referer = request.headers.get('Referer', '')
    base_path = i18n_url('content:sites_list')
    if str(base_path) not in referer:
        base_path = i18n_url('content:list')
    return dict(meta=meta, base_path=base_path, file_path=file_path)


def routes(app):
    skip_plugins = app.config['librarian.skip_plugins']
    return (
        # CONTENT
        ('content:list', content_list,
         'GET', '/', {}),
        ('content:sites_list', content_sites_list,
         'GET', '/sites/', {}),
        ('content:reader', content_reader,
         'GET', '/pages/<content_id>', {}),
        ('content:delete', remove_content_confirm,
         'GET', '/delete/<content_id>', {}),
        ('content:delete', remove_content,
         'POST', '/delete/<content_id>', {}),
        # This is a static file route and is shadowed by the static file server
        ('content:file', content_file,
         'GET', '/content/<content_path:re:[0-9a-f]{3}(/[0-9a-f]{3}){9}/[0-9a-f]{2}>/<filename:path>',  # NOQA
         dict(no_i18n=True, skip=skip_plugins)),
    )
