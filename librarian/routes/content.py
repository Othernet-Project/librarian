"""
content.py: routes related to content

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import stat

from bottle import request, view, abort, default_app

from ..lib import archive
from ..lib import downloads
from ..lib import send_file

__all__ = ('app', 'content_list', 'content_file', 'content_index',)

PREFIX = '/content'
CONTENT_ID = '<content_id:re:[0-9a-f]{32}>'


app = default_app()


@app.get(PREFIX + '/')
@view('content_list')
def content_list():
    """ Show list of content """
    return {'metadata': archive.get_content()}


@app.get(PREFIX + '/%s/<filename>' % CONTENT_ID)
def content_file(content_id, filename):
    """ Serve file from zipball with specified id """
    zippath = downloads.get_zip_path(content_id)
    try:
        metadata, content = downloads.get_file(zippath, filename)
    except KeyError:
        abort(404, 'Not found')
    size = metadata.file_size
    timestamp = os.stat(zippath)[stat.ST_MTIME]
    if filename.endswith('.html'):
        # Patch HTML with link to stylesheet
        size, content = downloads.patch_html(content)
    return send_file.send_file(content, filename, size, timestamp)


@app.get(PREFIX + '/%s/' % CONTENT_ID)
def content_index(content_id):
    """ Shorthand for /<content_id>/index.html """
    return content_file(content_id, 'index.html')

