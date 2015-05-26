"""
helpers.py: librarian core helper functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from functools import wraps

from bottle import request, abort

from ..core import content as content_mod
from ..core import metadata
from ..core.archive import Archive
from ..core.files import FileManager


def open_archive():
    conf = request.app.config
    return Archive.setup(conf['librarian.backend'],
                         request.db.main,
                         unpackdir=conf['content.unpackdir'],
                         contentdir=conf['content.contentdir'],
                         spooldir=conf['content.spooldir'],
                         meta_filename=conf['content.metadata'])


def init_filemanager():
    return FileManager(request.app.config['content.filedir'])


def with_content(func):
    @wraps(func)
    def wrapper(content_id, **kwargs):
        conf = request.app.config
        archive = open_archive()
        try:
            content = archive.get_single(content_id)
        except IndexError:
            abort(404)
        if not content:
            abort(404)
        content_dir = conf['content.contentdir']
        content_path = content_mod.to_path(content_id, prefix=content_dir)
        meta = metadata.Meta(content, content_path)
        return func(meta=meta, **kwargs)
    return wrapper
