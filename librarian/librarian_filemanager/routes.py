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
import functools
import subprocess

from bottle import request, abort, static_file, redirect, response
from bottle_utils.common import to_unicode
from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian.librarian_auth.decorators import login_required
from librarian.librarian_core.contrib.templates.renderer import template, view

from .files import FileManager


SHELL = '/bin/sh'


def init_filemanager():
    return FileManager(request.app.config['files.rootdir'])


def dictify_file_list(file_list):
    return [{
        'path': f[0],
        'name': f[1],
        'size': f[2],
    } for f in file_list]


@login_required(superuser_only=True)
@view('file_list')
def show_file_list(path=None):
    search = request.params.get('p')
    query = search or path or '.'
    resp_format = request.params.get('f', '')
    conf = request.app.config
    is_missing = False
    is_search = False
    files = init_filemanager()
    try:
        dir_contents = files.get_dir_contents(query)
        (path, relpath, dirs, file_list, readme) = dir_contents
    except files.DoesNotExist:
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
            is_missing = True
            relpath = '.'
            dirs = []
            file_list = []
            readme = _('This folder does not exist')
    except files.IsFileError as err:
        if resp_format == 'json':
            fstat = os.stat(query)
            response.content_type = 'application/json'
            return json.dumps(dict(
                name=os.path.basename(query),
                size=fstat[stat.ST_SIZE],
            ))
        options = {'download': request.params.get('filename', False)}
        return static_file(err.path, root=files.filedir, **options)

    up = os.path.normpath(os.path.join(files.get_full_path(query), '..'))
    up = os.path.relpath(up, conf['files.rootdir'])
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


def get_parent_url(path):
    files = init_filemanager()
    parent_dir = os.path.dirname(path)
    if parent_dir:
        parent_path = os.path.relpath(parent_dir, files.filedir)
    else:
        parent_path = ''

    return i18n_url('files:path', path=parent_path)


def go_to_parent(path):
    redirect(get_parent_url(path))


def guard_already_removed(func):
    @functools.wraps(func)
    def wrapper(path, **kwargs):
        files = init_filemanager()
        path = files.get_full_path(path)
        if not os.path.exists(path):
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
@view('remove_confirm')
def delete_path_confirm(path):
    cancel_url = request.headers.get('Referer', get_parent_url(path))
    return dict(item_name=os.path.basename(path), cancel_url=cancel_url)


@csrf_protect
@guard_already_removed
@view('feedback')
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

    # Translators, used as page title of successful file removal feedback
    page_title = _("File removed")
    # Translators, used as message of successful file removal feedback
    message = _("File successfully removed.")
    return dict(status='success',
                page_title=page_title,
                message=message,
                redirect_url=get_parent_url(path),
                redirect_target=_("Files"))


def rename_path(path):
    new_name = request.forms.get('name')
    if not new_name:
        go_to_parent(path)
    new_name = os.path.normpath(new_name)
    new_path = os.path.join(os.path.dirname(path), new_name)
    shutil.move(path, new_path)
    go_to_parent(path)


def run_path(path):
    callargs = [SHELL, path]
    proc = subprocess.Popen(callargs,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    ret = proc.returncode
    return ret, out, err


@login_required(superuser_only=True)
def handle_file_action(path):
    action = request.forms.get('action')
    files = init_filemanager()
    path = files.get_full_path(path)
    if action == 'rename':
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


def routes(config):
    return (
        ('files:list', show_file_list,
         'GET', '/files/', dict(unlocked=True)),
        ('files:delete_confirm', delete_path_confirm,
         'GET', '/files/<path:path>/delete/', dict(unlocked=True)),
        ('files:delete', delete_path,
         'POST', '/files/<path:path>/delete/', dict(unlocked=True)),
        ('files:path', show_file_list,
         'GET', '/files/<path:path>', dict(unlocked=True)),
        ('files:action', handle_file_action,
         'POST', '/files/<path:path>', dict(unlocked=True)),
    )
