"""
files.py: list files in files directory

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
from collections import namedtuple

from bottle import request


Pathdata = namedtuple('Pathdata', ('path', 'name', 'size'))


class IsFileError(Exception):
    def __init__(self, msg, path):
        self.path = path
        super(IsFileError, self).__init__(msg)


class DoesNotExist(Exception):
    pass


def get_file_dir():
    return os.path.normpath(request.app.config['content.filedir'])


def get_full_path(path):
    filedir = get_file_dir()
    path = os.path.normpath(path.replace('..', '.'))
    full = os.path.normpath(os.path.join(filedir, path))
    if full.startswith(filedir):
        return full
    return filedir


def get_search_results(s):
    filedir = get_file_dir()
    rdirs = []
    rfiles = []
    s = s.lower()
    for root, dirs, files in os.walk(filedir):
        for d in dirs:
            if d.startswith('.'):
                continue
            if s in d.lower():
                rdirs.append(Pathdata(
                    os.path.relpath(os.path.join(root, d), filedir), d, 0))
        for f in files:
            if f.startswith('.'):
                continue
            if s in f.lower():
                rfiles.append(Pathdata(
                    os.path.relpath(os.path.join(root, f), filedir), f, 0))
    return rdirs, rfiles


def get_dir_contents(path):
    filedir = get_file_dir()
    dirs = []
    files = []
    readme = ''
    path = get_full_path(path)
    if not os.path.exists(path):
        raise DoesNotExist('Path not found %s' % path)
    if not os.path.isdir(path):
        raise IsFileError('Path is a file', os.path.relpath(path, filedir))
    for p in os.listdir(path):
        if p.startswith('.'):
            if p == '.README':
                with open(os.path.join(path, p), 'r') as f:
                    readme = f.read()
            continue
        p = os.path.normpath(os.path.join(path, p))
        if os.path.isdir(p):
            d = Pathdata(
                os.path.relpath(p, filedir),
                os.path.basename(p),
                0)
            dirs.append(d)
        else:
            f = Pathdata(
                os.path.relpath(p, filedir),
                os.path.basename(p),
                os.stat(p).st_size)
            files.append(f)
    return (
        path,
        os.path.relpath(path, filedir),
        sorted(dirs, key=lambda x: x.name),
        sorted(files, key=lambda x: x.name),
        readme)
