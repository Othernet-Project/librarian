"""
files.py: routes related to files section

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import static_file
from bottle_utils.html import urlunquote
from bottle_utils.i18n import lazy_gettext as _
from streamline import NonIterableRouteBase, XHRPartialRoute, TemplateFormRoute

from ..core.contrib.templates.renderer import template
from ..data.manager import Manager
from ..data.meta.contenttypes import ContentTypes
from ..forms.filemanager import DeleteForm
from ..helpers.filemanager import get_parent_url, find_root, get_thumb_path
from ..presentation.paginator import Paginator
from ..utils.route_mixins import CSRFRouteMixin


class FileRouteMixin(object):
    #: Key under which to look for the requested view in query parameters
    VIEW_KEY = 'view'
    #: Special purpose views
    UPDATES_VIEW = 'updates'
    #: List of allowed view names
    VALID_VIEWS = ContentTypes.names() + [UPDATES_VIEW]
    #: In case an invalid view is specified, or none, fallback to this view
    DEFAULT_VIEW = ContentTypes.GENERIC

    def __init__(self, *args, **kwargs):
        super(FileRouteMixin, self).__init__(*args, **kwargs)
        self.manager = Manager()

    def has_requested_view(self):
        return self.VIEW_KEY in self.request.params

    def get_view(self):
        view = self.request.params.get(self.VIEW_KEY, None)
        # use default view if it wasn't specfied explicitly or it's not valid
        if view not in self.VALID_VIEWS:
            return self.DEFAULT_VIEW
        return view

    def unquoted(self, key):
        try:
            value = self.request.params[key]
        except KeyError:
            return None
        else:
            return urlunquote(value).strip()


class List(FileRouteMixin, XHRPartialRoute):
    path = '/files/<path:safepath>'
    template_name = 'filemanager/main'
    partial_template_name = 'filemanager/_main'
    template_func = template

    QUERY_KEY = 'q'
    HIDDEN_KEY = 'hidden'
    SELECTED_KEY = 'selected'

    def paginate(self, count):
        # parse pagination params
        page = Paginator.parse_page(self.request.params)
        per_page = Paginator.parse_per_page(self.request.params)
        return Paginator(count, page, per_page)

    def search(self, path, show_hidden):
        default_lang = self.request.user.options.get('content_language')
        language = self.request.params.get('language', default_lang)
        return self.manager.search(path,
                                   show_hidden=show_hidden,
                                   language=language)

    def updates(self, path, show_hidden):
        count = self.manager.descendants(path,
                                         count=True,
                                         show_hidden=show_hidden)
        pager = self.paginate(count)
        result = self.manager.descendants(path,
                                          offset=pager.offset,
                                          limit=pager.limit,
                                          show_hidden=show_hidden)
        result.update(pager=pager)
        return result

    def list(self, path, show_hidden, content_type, selected):
        try:
            return self.manager.list(path,
                                     content_type=content_type,
                                     selected=selected,
                                     show_hidden=show_hidden)
        except self.manager.InvalidQuery:
            self.abort(404)

    def promote_view(self, view, parent):
        # for explicitly chosen views, no auto-promition will be applied
        if self.has_requested_view():
            return view
        # when no view was chosen, auto-promition is allowed
        available_views = parent.meta.content_type_names
        if ContentTypes.HTML in available_views:
            return ContentTypes.HTML
        # no better match, stick with original plan
        return view

    def get(self, path):
        view = self.get_view()
        path = self.unquoted(self.QUERY_KEY) or path or self.manager.get_root()
        show_hidden = self.request.params.get(self.HIDDEN_KEY, 'no') == 'yes'
        is_search = self.QUERY_KEY in self.request.params
        selected = self.unquoted(self.SELECTED_KEY)
        if is_search:
            result = self.search(path, show_hidden)
        elif view == self.UPDATES_VIEW:
            result = self.updates(path, show_hidden)
        else:
            result = self.list(path, show_hidden, view, selected)
        # perform view promotion, if available
        view = self.promote_view(view, result['current'])
        result.update(is_search=is_search,
                      view=view,
                      selected_name=selected)
        return result


class Details(FileRouteMixin, XHRPartialRoute):
    path = '/details/<path:safepath>'
    template_name = 'filemanager/info'
    partial_template_name = 'filemanager/_info'
    template_func = template

    META_KEY = 'info'

    def get(self, path):
        path = path or self.manager.get_root()
        view = self.get_view()
        file_path = os.path.join(path, self.unquoted(self.META_KEY))
        try:
            fso = self.manager.get(file_path, content_type=view)
        except self.manager.InvalidQuery:
            # There is no such file
            self.abort(404)
        else:
            return dict(entry=fso, view=view)


class Direct(NonIterableRouteBase):
    path = '/direct/<path:safepath>'

    def get(self, path):
        try:
            root = find_root(path)
        except RuntimeError:
            self.abort(404, _("File not found."))
        else:
            download = self.request.params.get('filename', False)
            return static_file(path, root=root, download=download)


class Delete(CSRFRouteMixin, TemplateFormRoute):
    path = '/delete/<path:safepath>'
    template_func = template
    template_name = 'filemanager/remove_confirm'
    form_factory = DeleteForm

    def __init__(self, *args, **kwargs):
        super(Delete, self).__init__(*args, **kwargs)
        self.manager = Manager()

    def get_unbound_form(self):
        form_factory = self.get_form_factory()
        initial = dict(path=self.request.url_args['path'])
        return form_factory(initial)

    def get_context(self):
        context = super(Delete, self).get_context()
        path = self.request.url_args['path']
        cancel_url = self.request.headers.get('Referer', get_parent_url(path))
        context.update(path=path,
                       item_name=os.path.basename(path),
                       cancel_url=cancel_url)
        return context

    def already_removed(self, path):
        # Translators, used as page title when a file's removal is
        # retried, but it was already deleted before
        page_title = _("File already removed")
        # Translators, used as message when a file's removal is
        # retried, but it was already deleted before
        message = _("The specified file has already been removed.")
        body = self.template_func('ui/feedback.tpl',
                                  status='success',
                                  page_title=page_title,
                                  message=message,
                                  redirect_url=get_parent_url(path),
                                  redirect_target=_("Files"))
        return self.HTTPResponse(body)

    def removal_succeeded(self, path):
        # Translators, used as page title of successful file removal feedback
        page_title = _("File removed")
        # Translators, used as message of successful file removal feedback
        message = _("File successfully removed.")
        body = self.template_func('ui/feedback.tpl',
                                  status='success',
                                  page_title=page_title,
                                  message=message,
                                  redirect_url=get_parent_url(path),
                                  redirect_target=_("file list"))
        return self.HTTPResponse(body)

    def removal_failed(self, path):
        # Translators, used as page title of unsuccessful file removal feedback
        page_title = _("File not removed")
        # Translators, used as message of unsuccessful file removal feedback
        message = _("File could not be removed.")
        body = self.template_func('ui/feedback.tpl',
                                  status='error',
                                  page_title=page_title,
                                  message=message,
                                  redirect_url=get_parent_url(path),
                                  redirect_target=_("file list"))
        return self.HTTPResponse(body)

    def form_invalid(self, path):
        return self.already_removed(path)

    def form_valid(self, path):
        path = self.form.processed_data['path']
        (success, error) = self.manager.remove(path)
        if success:
            return self.removal_succeeded(path)
        return self.removal_failed(path)


class Thumb(NonIterableRouteBase):
    path = '/thumb/<path:safepath>'

    def get(self, path):
        url = None
        thumb_path = get_thumb_path(path)
        if thumb_path:
            url = self.app.get_url('filemanager:direct', path=thumb_path)
        return dict(url=url)
