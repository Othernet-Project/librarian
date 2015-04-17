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
try:
    from io import BytesIO as StringIO
except ImportError:
    from cStringIO import StringIO

from bottle import (
    request, mako_view as view, abort, default_app, static_file, redirect,
    response, mako_template as template)
from bottle_utils.ajax import roca_view
from bottle_utils.common import to_unicode
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ..core import files
from ..core import archive
from ..core import downloads
from ..core import metadata

from ..lib import auth
from ..lib import send_file
from ..lib.pager import Pager

from ..utils import patch_content

from .helpers import with_content


app = default_app()


def filter_content(multipage=None):
    conf = request.app.config
    query = request.params.getunicode('q', '').strip()

    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('lang', default_lang)
    request.user.options['content_language'] = lang

    try:
        tag = int(request.params.get('tag'))
    except (TypeError, ValueError):
        tag = None
        tag_name = None

    if query:
        total_items = archive.get_search_count(query,
                                               tag=tag,
                                               lang=lang,
                                               multipage=multipage)
    else:
        total_items = archive.get_count(tag=tag,
                                        lang=lang,
                                        multipage=multipage)

    if tag:
        try:
            tag_name = archive.get_tag_name(tag)['name']
        except (IndexError, KeyError):
            abort(404, _('Specified tag was not found'))

    # We will use a list of fake content (just a normal list of numbers) to
    # trick the pager into calculating correct page numbers
    pager = Pager(total_items, pid='content')
    pager.get_paging_params()

    if query:
        metas = archive.search_content(query,
                                       pager.offset,
                                       pager.per_page,
                                       tag=tag,
                                       lang=lang,
                                       multipage=multipage)
    else:
        metas = archive.get_content(pager.offset,
                                    pager.per_page,
                                    tag=tag,
                                    lang=lang,
                                    multipage=multipage)

    cover_dir = conf['content.covers']

    metas = [metadata.Meta(m, cover_dir, downloads.get_zip_path(m['md5']))
             for m in metas]

    return dict(
        metadata=metas,
        total_items=total_items,
        pager=pager,
        vals=request.params.decode(),
        query=query,
        lang=dict(lang=lang),
        tag=tag_name,
        tag_id=tag,
        tag_cloud=archive.get_tag_cloud()
    )


@roca_view('content_list', '_content_list', template_func=template)
def content_list():
    """ Show list of content """
    result = filter_content()
    result.update({'base_path': i18n_url('content:list'),
                   'page_title': _('Library')})
    return result


@roca_view('content_list', '_content_list', template_func=template)
def content_sites_list():
    """ Show list of multipage content only """
    result = filter_content(multipage=True)
    result.update({'base_path': i18n_url('content:sites_list'),
                   'page_title': _('Sites')})
    return result


@auth.login_required(next_to='/')
@view('remove_error')
def remove_content(content_id):
    """ Delete a single piece of content from archive """
    redir_path = i18n_url('content:list')
    failed = archive.remove_from_archive([content_id])
    if failed:
        assert len(failed) == 1, 'Expected only one failure'
        return dict(redirect=redir_path)
    redirect(redir_path)


def content_file(content_id, filename):
    """ Serve file from zipball with specified id """
    zippath = downloads.get_zip_path(content_id)
    try:
        metadata, content = downloads.get_file(zippath, filename, no_read=True)
    except downloads.ContentError as err:
        logging.error(err)
        abort(404)
    size = metadata.file_size
    timestamp = os.stat(zippath)[stat.ST_MTIME]
    if filename.endswith('.html') and archive.needs_formatting(content_id):
        logging.debug("Patching HTML file '%s' with Librarian stylesheet" % (
                      filename))
        size, content = patch_content.patch(content.read())
        content = StringIO(content.encode('utf8'))
    return send_file.send_file(content, filename, size, timestamp)


def content_zipball(content_id):
    """ Serve zipball with specified id """
    zippath = downloads.get_zip_path(content_id)
    dirname = os.path.dirname(zippath)
    filename = os.path.basename(zippath)
    return static_file(filename, root=dirname, download=True)


@view('reader')
@with_content
def content_reader(meta):
    """ Loads the reader interface """
    archive.add_view(meta.md5)
    referer = request.headers.get('Referer', '')
    base_path = i18n_url('content:sites_list')
    content_path = request.params.get('path', meta.entry_point)
    content_path = meta.entry_point if content_path == '/' else content_path
    if str(base_path) not in referer:
        base_path = i18n_url('content:list')
    return dict(meta=meta, base_path=base_path, content_path=content_path)


def cover_image(path):
    config = request.app.config
    covers = config['content.covers']
    return static_file(path, root=covers, download=os.path.basename(path))


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
            path, relpath, dirs, file_list, readme = files.get_dir_contents(
                path)
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
            return static_file(err.path, root=files.get_file_dir(), **options)
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
    filedir = files.get_file_dir()
    redirect(i18n_url('files:path', path=os.path.relpath(
        os.path.dirname(path), filedir)))


def delete_path(path):
    filedir = files.get_file_dir()
    if not os.path.exists(path):
        abort(404)
    if os.path.isdir(path):
        if path == filedir:
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
