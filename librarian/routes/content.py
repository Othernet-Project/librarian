"""
content.py: routes related to content

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat
import json
import shutil
import logging
import subprocess

from bottle import request, abort, default_app, static_file, redirect, response
from bottle_utils.ajax import roca_view
from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.common import to_unicode
from bottle_utils.i18n import lazy_gettext as _, i18n_url
from fdsend import send_file

from ..core import content
from ..core import metadata
from ..core import zipballs

from ..lib import auth
from ..lib.paginator import Paginator

from ..utils.cache import cached
from ..utils.template import template, view
from ..utils.core_helpers import open_archive, init_filemanager, with_content


app = default_app()


@cached(prefix='content')
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


@auth.login_required(next_to='/')
@csrf_token
@view('remove_confirm')
def remove_content_confirm(content_id):
    archive = open_archive()
    cancel_url = request.headers.get('Referer', i18n_url('content:list'))
    return dict(cancel_url=cancel_url,
                content=archive.get_single(content_id))


@auth.login_required(next_to='/')
@csrf_protect
def remove_content(content_id):
    """ Delete a single piece of content from archive """
    redir_path = i18n_url('content:list')
    archive = open_archive()
    archive.remove_from_archive([content_id])
    request.app.exts.cache.invalidate(prefix='content')
    # Translators, used as page title of successful content removal feedback
    page_title = _("Content removed")
    # Translators, used as message of successful content removal feedback
    sub_message = _("Content successfully removed.")
    return template('feedback',
                    status='success',
                    page_title=page_title,
                    main_message=page_title,
                    sub_message=sub_message,
                    redirect=redir_path)


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


def dictify_file_list(file_list):
    return [{
        'path': f[0],
        'name': f[1],
        'size': f[2],
    } for f in file_list]


@view('file_list')
def show_file_list(path='.'):
    search = request.params.get('p')
    resp_format = request.params.get('f', '')
    conf = request.app.config
    is_missing = False
    is_search = False
    files = init_filemanager()
    if search:
        relpath = '.'
        up = ''
        dirs, file_list = files.get_search_results(search)
        is_search = True
        if not len(file_list) and len(dirs) == 1:
            redirect(i18n_url('files:path',
                              path=dirs[0].path.replace('\\', '/')))
        if not dirs and not file_list:
            is_missing = True
            readme = _('The files you were looking for could not be found')
        else:
            readme = _('This list represents the search results')
    else:
        is_search = False
        try:
            dir_contents = files.get_dir_contents(path)
            (path, relpath, dirs, file_list, readme) = dir_contents
        except files.DoesNotExist:
            is_missing = True
            relpath = '.'
            dirs = []
            file_list = []
            readme = _('This folder does not exist')
        except files.IsFileError as err:
            if resp_format == 'json':
                fstat = os.stat(path)
                response.content_type = 'application/json'
                return json.dumps(dict(
                    name=os.path.basename(path),
                    size=fstat[stat.ST_SIZE],
                ))
            options = {'download': request.params.get('filename', False)}
            return static_file(err.path, root=files.filedir, **options)
    up = os.path.normpath(os.path.join(path, '..'))
    up = os.path.relpath(up, conf['content.filedir'])
    if resp_format == 'json':
        response.content_type = 'application/json'
        return json.dumps(dict(
            dirs=dirs,
            files=dictify_file_list(file_list),
            readme=to_unicode(readme),
            is_missing=is_missing,
            is_search=is_search,
        ))
    return dict(path=relpath, dirs=dirs, files=file_list, up=up, readme=readme,
                is_missing=is_missing, is_search=is_search)


def go_to_parent(path):
    files = init_filemanager()
    parent_path = os.path.relpath(os.path.dirname(path), files.filedir)
    redirect(i18n_url('files:path', path=parent_path))


def delete_path(path):
    files = init_filemanager()
    if not os.path.exists(path):
        abort(404)
    if os.path.isdir(path):
        if path == files.filedir:
            # FIXME: handle this case
            abort(400)
        shutil.rmtree(path)
    else:
        os.unlink(path)
    go_to_parent(path)


def rename_path(path):
    new_name = request.forms.get('name')
    if not new_name:
        go_to_parent(path)
    new_name = os.path.normpath(new_name)
    new_path = os.path.join(os.path.dirname(path), new_name)
    os.rename(path, new_path)
    go_to_parent(path)


def run_path(path):
    callargs = [path]
    proc = subprocess.Popen(callargs, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    ret = proc.returncode
    return ret, out, err


def handle_file_action(path):
    action = request.forms.get('action')
    files = init_filemanager()
    path = files.get_full_path(path)
    if action == 'delete':
        delete_path(path)
    elif action == 'rename':
        rename_path(path)
    elif action == 'exec':
        if os.path.splitext(path)[1] != '.sh':
            # For now we only support running BASH scripts
            abort(400)
        logging.info("Running script '%s'", path)
        ret, out, err = run_path(path)
        logging.debug("Script '%s' finished with return code %s", path, ret)
        return template('exec_result', ret=ret, out=out, err=err)
    else:
        abort(400)
