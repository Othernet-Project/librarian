"""
content.py: routes related to content

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat
import math
import json
import shutil
import logging

from bottle import (
    request, view, abort, default_app, static_file, redirect, response)

from ..lib import archive
from ..lib import downloads
from ..lib import send_file
from ..lib import files
from ..lib import i18n

__all__ = ('app', 'content_list', 'content_file', 'content_index',)

PREFIX = ''
CONTENT_ID = '<content_id:re:[0-9a-f]{32}>'


app = default_app()


@app.get(PREFIX + '/')
@view('content_list')
def content_list():
    """ Show list of content """
    try:
        f_per_page = int(request.params.get('c', 1))
    except ValueError as e:
        f_per_page = 1
    f_per_page = max(1, min(4, f_per_page))
    try:
        page = int(request.params.get('p', 1))
    except ValueError:
        page = 1
    query = request.params.getunicode('q', '').strip()

    per_page = f_per_page * 20

    if query:
        total_items = archive.get_search_count(query)
    else:
        total_items = archive.get_count()

    total_pages = math.ceil(total_items / per_page)
    page = max(1, min(total_pages, page))
    offset = (page - 1) * per_page

    if query:
        metadata = archive.search_content(query, offset, per_page)
    else:
        metadata = archive.get_content(offset, per_page)

    return {
        'metadata': metadata,
        'total_items': total_items,
        'total_pages': total_pages,
        'per_page': per_page,
        'f_per_page': f_per_page,
        'page': page,
        'vals': request.params.decode(),
        'query': query,
    }


@app.get(PREFIX + '/pages/%s/<filename:path>' % CONTENT_ID)
def content_file(content_id, filename):
    """ Serve file from zipball with specified id """
    zippath = downloads.get_zip_path(content_id)
    try:
        metadata, content = downloads.get_file(zippath, filename)
    except KeyError:
        logging.debug("File '%s' not found in '%s'" % (filename, zippath))
        abort(404, 'Not found')
    size = metadata.file_size
    timestamp = os.stat(zippath)[stat.ST_MTIME]
    if filename.endswith('.html'):
        logging.debug("Patching HTML file '%s' with Librarian stylesheet" % (
                      filename))
        # Patch HTML with link to stylesheet
        size, content = downloads.patch_html(content)
    return send_file.send_file(content, filename, size, timestamp)


@app.get(PREFIX + '/pages/%s/' % CONTENT_ID)
def content_index(content_id):
    """ Shorthand for /<content_id>/index.html """
    archive.add_view(content_id)
    return content_file(content_id, 'index.html')


def dictify_file_list(file_list):
    return [{
        'path': f[0],
        'name': f[1],
        'size': f[2],
    } for f in file_list]


@app.get(PREFIX + '/files/')
@app.get(PREFIX + '/files/<path:path>')
@view('file_list')
def show_file_list(path='.'):
    path = request.params.get('p', path)
    resp_format = request.params.get('f', '')
    try:
        path, relpath, dirs, file_list, readme = files.get_dir_contents(path)
    except files.DoesNotExist:
        if path == '.':
            if resp_format == 'json':
                response.content_type = 'application/json'
                return json.dumps(dict(
                    dirs=dirs,
                    files=dictify_file_list(file_list),
                    readme=readme
                ))
            return dict(path='.', dirs=[], files=[], up='.', readme='')
        abort(404)
    except files.IsFileError as err:
        if resp_format == 'json':
            fstat = os.stat(path)
            response.content_type = 'application/json'
            return json.dumps(dict(
                name=os.path.basename(path),
                size=fstat[stat.ST_SIZE],
            ))
        return static_file(err.path, root=files.get_file_dir())
    up = os.path.normpath(os.path.join(path, '..'))
    if resp_format == 'json':
        response.content_type = 'application/json'
        return json.dumps(dict(
            dirs=dirs,
            files=dictify_file_list(file_list),
            readme=readme
        ))
    return dict(path=relpath, dirs=dirs, files=file_list, up=up, readme=readme)


def go_to_parent(path):
    filedir= files.get_file_dir()
    redirect(i18n.i18n_path('/files/') + os.path.relpath(
        os.path.dirname(path), filedir))


def delete_path(path):
    filedir= files.get_file_dir()
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
    filedir= files.get_file_dir()
    new_name = request.forms.get('name')
    if not new_name:
        go_to_parent(path)
    new_name = os.path.normpath(new_name)
    new_path =  os.path.join(os.path.dirname(path), new_name)
    os.rename(path, new_path)
    go_to_parent(path)


@app.post(PREFIX + '/files/<path:path>')
def handle_file_action(path):
    action = request.forms.get('action')
    path = files.get_full_path(path)
    if action == 'delete':
        delete_path(path)
    elif action == 'rename':
        rename_path(path)
    else:
        abort(400)
