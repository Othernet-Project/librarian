"""
files.py: routes related to files section

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import functools

from bottle import request, abort, static_file
from bottle_utils.ajax import roca_view
from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.html import urlunquote, quoted_url
from bottle_utils.i18n import lazy_gettext as _
from streamline import XHRPartialRoute

from ..core.exts import ext_container as exts
from ..core.contrib.cache.decorators import cached
from ..core.contrib.templates.renderer import template, view
from ..data.facets.facets import FacetTypes
from ..data.facets.utils import (get_facets,
                                 get_facet_types,
                                 is_facet_valid,
                                 find_html_index)
from ..data.manager import Manager
from ..helpers.filemanager import (get_parent_path,
                                   get_parent_url,
                                   find_root,
                                   get_thumb_path)
from ..presentation.paginator import Paginator
from ..utils.route_mixins import CSRFRouteMixin


class FileList(XHRPartialRoute):
    template_name = 'filemanager/main'
    partial_template_name = 'filemanager/_main'
    template_func = template

    ROOT_PATH = '.'
    QUERY_KEY = 'q'
    SHOW_HIDDEN_KEY = 'hidden'
    SELECTED_KEY = 'selected'
    VIEW_KEY = 'view'
    VALID_VIEWS = ['updates'] + FacetTypes.names()
    DEFAULT_VIEW = FacetTypes.HTML
    UNFILTERED_FACET_TYPES = (FacetTypes.GENERIC, FacetTypes.UPDATES)

    def __init__(self, *args, **kwargs):
        super(FileList, self).__init__(*args, **kwargs)
        self.manager = Manager()

    def unquoted(self, key):
        try:
            value = self.request.params[key]
        except KeyError:
            return None
        else:
            return urlunquote(value).strip()

    @property
    def is_search(self):
        return self.QUERY_KEY in self.request.params

    @property
    def query(self):
        return self.unquoted(self.QUERY_KEY)

    @property
    def selected(self):
        return self.unquoted(self.SELECTED_KEY)

    @property
    def show_hidden(self):
        return self.request.params.get(self.SHOW_HIDDEN_KEY, 'no') == 'yes'

    def set_view(self, context, relpaths):
        view = self.request.params.get(self.VIEW_KEY, None)
        # use html view if it wasn't specfied explicitly
        if not view or view == FacetTypes.HTML:
            context['index_file'] = find_html_index(relpaths, any_html=False)
        # if no index file matches, fall back to generic view
        if not view and not context['index_file']:
            view = FacetTypes.GENERIC
        # if requested view is not valid, fall back to generic view
        if view not in self.VALID_VIEWS:
            view = FacetTypes.GENERIC
        # update context with best matching view
        context.update(view=view)

    def get_file_list(self, query):
        if self.is_search:
            result = self.manager.search(query, self.show_hidden)
            relpath = self.ROOT_PATH if not result['is_match'] else query
        else:
            result = self.manager.list(query, self.show_hidden)
            relpath = query
            if not result['success']:
                self.abort(404)
        return dict(path=relpath,
                    current=self.manager.get(relpath),
                    up=get_parent_path(relpath),
                    dirs=result['dirs'],
                    files=result['files'])

    @cached(prefix='descendants', timeout=300)
    def __get_update_count(self, path, span):
        result = self.manager.list_descendants(path,
                                               count=True,
                                               span=span,
                                               entry_type=0)
        return result['count']

    def fetch_updates(self, context):
        span = exts.config['changelog.span']
        count = self.__get_update_count(context['path'], span)
        # parse pagination params
        page = Paginator.parse_page(request.params)
        per_page = Paginator.parse_per_page(request.params)
        pager = Paginator(count, page, per_page)
        (offset, limit) = pager.items
        results = self.manager.list_descendants(context['path'],
                                                offset=offset,
                                                limit=limit,
                                                order='-create_time',
                                                span=span,
                                                entry_type=0,
                                                show_hidden=False)
        context.update(pager=pager, files=results['files'])

    def get(self, path):
        path = path or self.ROOT_PATH
        ctx = self.get_file_list(self.query or path)
        relpaths = [f.rel_path for f in ctx['files']]
        ctx.update(is_search=self.is_search,
                   selected=self.selected,
                   facet_types=get_facet_types(relpaths))
        self.set_view(ctx, relpaths)
        if not self.is_search:
            # updates override the files list with a custom one
            if ctx['view'] == FacetTypes.UPDATES:
                self.fetch_updates(ctx)
            # limit the list of files to only those that can be handled
            # within the chosen view
            if ctx['view'] not in self.UNFILTERED_FACET_TYPES:
                ctx['files'] = [f for f in ctx['files']
                                if is_facet_valid(f.rel_path, ctx['view'])]
        return ctx


@roca_view('filemanager/info', 'filemanager/_info', template_func=template)
def show_info_view(path, view, meta, defaults):
    file_path = os.path.join(path, meta)
    success, fso = request.app.supervisor.exts.fsal.get_fso(file_path)
    if not success:
        # There is no such file
        abort(404)
    try:
        facets = list(get_facets((file_path,), facet_type=view))[0]
    except IndexError:
        abort(404)
    fso.facets = facets
    defaults['entry'] = fso
    return defaults


def show_view(path, view, defaults):
    defaults.update(get_file_list(path))
    meta = request.query.get('info')
    if meta:
        return show_info_view(path, view, urlunquote(meta), defaults)
    return show_list_view(path, view, defaults)


def direct_file(path):
    path = urlunquote(path)
    try:
        root = find_root(path)
    except RuntimeError:
        abort(404, _("File not found."))

    download = request.params.get('filename', False)
    return static_file(path, root=root, download=download)


def guard_already_removed(func):
    @functools.wraps(func)
    def wrapper(path, **kwargs):
        manager = Manager()
        if not manager.exists(path):
            # Translators, used as page title when a file's removal is
            # retried, but it was already deleted before
            title = _("File already removed")
            # Translators, used as message when a file's removal is
            # retried, but it was already deleted before
            message = _("The specified file has already been removed.")
            return template('feedback',
                            status='success',
                            page_title=title,
                            message=message,
                            redirect_url=get_parent_url(path),
                            redirect_target=_("Files"))
        return func(path=path, **kwargs)
    return wrapper


@csrf_token
@guard_already_removed
@view('filemanager/remove_confirm')
def delete_path_confirm(path):
    cancel_url = request.headers.get('Referer', get_parent_url(path))
    return dict(item_name=os.path.basename(path), cancel_url=cancel_url)


@csrf_protect
@guard_already_removed
@view('ui/feedback')
def delete_path(path):
    manager = Manager()
    (success, error) = manager.remove(path)
    if success:
        # Translators, used as page title of successful file removal feedback
        page_title = _("File removed")
        # Translators, used as message of successful file removal feedback
        message = _("File successfully removed.")
        return dict(status='success',
                    page_title=page_title,
                    message=message,
                    redirect_url=get_parent_url(path),
                    redirect_target=_("file list"))

    # Translators, used as page title of unsuccessful file removal feedback
    page_title = _("File not removed")
    # Translators, used as message of unsuccessful file removal feedback
    message = _("File could not be removed.")
    return dict(status='error',
                page_title=page_title,
                message=message,
                redirect_url=get_parent_url(path),
                redirect_target=_("file list"))


def retrieve_thumb_url(path, defaults):
    thumb_url = None
    thumb_path = get_thumb_path(urlunquote(request.query.get('target')))
    if thumb_path:
        thumb_url = quoted_url('files:direct', path=thumb_path)
    else:
        facet_type = request.query.get('facet', 'generic')
        try:
            facet = defaults['facets'][facet_type]
        except KeyError:
            pass
        else:
            cover = facet.get('cover')
            if cover:
                cover_path = os.path.join(facet['path'], cover)
                thumb_url = quoted_url('files:direct',
                                       path=cover_path)

    return dict(url=thumb_url)

