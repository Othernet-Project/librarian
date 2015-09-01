"""
content.py: routes related to content

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools
import os

from bottle import request, abort, static_file
from bottle_utils.ajax import roca_view
from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.i18n import lazy_gettext as _, i18n_url
from fdsend import send_file

from librarian.librarian_auth.decorators import login_required
from librarian.librarian_cache.decorators import cached
from librarian.librarian_core.contrib.templates.renderer import template, view

from ..decorators import with_content
from ..helpers import open_archive
from ..library import content
from ..library import metadata
from ..library import zipballs
from ..paginator import Paginator


@cached(prefix='content', timeout=300)
def filter_content(query, lang, tag, content_type):
    conf = request.app.config
    archive = open_archive()
    raw_metas = archive.get_content(terms=query,
                                    lang=lang,
                                    tag=tag,
                                    content_type=content_type)
    contentdir = conf['library.contentdir']
    metas = [metadata.Meta(meta, content.to_path(meta['md5'], contentdir))
             for meta in raw_metas]
    return metas


@roca_view('content_list', '_content_list', template_func=template)
def content_list():
    """ Show list of content """
    # parse search query
    query = request.params.getunicode('q', '').strip()
    # parse language filter
    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang
    # parse content type filter
    content_type = request.params.get('content_type')
    if content_type not in metadata.CONTENT_TYPES:
        content_type = None
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
    metas = filter_content(query, lang, tag, content_type)
    pager = Paginator(metas, page, per_page)
    return dict(metadata=pager.items,
                pager=pager,
                vals=request.params.decode(),
                query=query,
                lang=dict(lang=lang),
                content_types=metadata.CONTENT_TYPES,
                chosen_content_type=content_type,
                tag=tag_name,
                tag_id=tag,
                tag_cloud=archive.get_tag_cloud(),
                base_path=i18n_url('content:list'),
                view=request.params.get('view'))


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


@login_required(next_to='/')
@csrf_token
@guard_already_removed
@view('remove_confirm')
def remove_content_confirm(content):
    return dict(content=content, cancel_url=i18n_url('content:list'))


@login_required(next_to='/')
@csrf_protect
@guard_already_removed
@view('feedback')
def remove_content(content):
    """ Delete a single piece of content from archive """
    archive = open_archive()
    archive.remove_from_archive([content.md5])
    request.app.supervisor.exts.cache.invalidate(prefix='content')
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
    content_dir = request.app.config['library.contentdir']
    content_root = os.path.join(content_dir, content_path)
    return static_file(filename, root=content_root)


@cached(prefix='zipball')
def prepare_zipball(content_id):
    content_dir = request.app.config['library.contentdir']
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
    # as mixed content is possible in zipballs, it is allowed to specify which
    # content type is being viewed now explicitly, falling back to the first
    # one found in the content object
    content_type = request.params.get('content_type')
    if content_type is None:
        # pick first available content type present in content object as it was
        # not specified
        content_type = meta.content_type_names[0]

    return dict(meta=meta,
                base_path=i18n_url('content:list'),
                chosen_content_type=content_type,
                chosen_path=request.params.get('path'))
