"""
files.py: routes related to files section

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

from bottle import request, abort, static_file, redirect, response
from bottle_utils.common import to_unicode
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ..utils.template import template, view
from ..utils.core_helpers import init_filemanager


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
    shutil.move(path, new_path)
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


def routes(app):
    return (
        ('files:list', show_file_list,
         'GET', '/files/', dict(unlocked=True)),
        ('files:path', show_file_list,
         'GET', '/files/<path:path>', dict(unlocked=True)),
        ('files:action', handle_file_action,
         'POST', '/files/<path:path>', dict(unlocked=True)),
    )
