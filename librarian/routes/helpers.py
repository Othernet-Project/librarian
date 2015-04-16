"""
helpers.py: common helper functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from functools import wraps

from bottle import request, abort

from ..core import downloads
from ..core import metadata
from ..core.archive import Archive


def open_archive():
    return Archive.setup(request.app.config['librarian.backend'],
                         request.db.main,
                         content_dir=request.app.config['content.contentdir'])


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
        zip_path = downloads.get_zip_path(content_id)
        assert zip_path is not None, 'Expected zipball to exist'
        meta = metadata.Meta(content, conf['content.covers'], zip_path)
        return func(meta=meta, **kwargs)
    return wrapper
