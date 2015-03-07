"""
send_file.py: functions for sending static files

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import time
import mimetypes

from gevent import spawn
from bottle import (HTTPResponse, HTTPError, parse_date, parse_range_header,
                    request)


__all__ = ('MIME_TYPES', 'EXTENSIONS', 'DEFAULT_TYPE', 'get_mimetype',
           'format_ts', 'iter_read_range', 'send_file',)


# We only neeed MIME types for files Outernet will broadcast
MIME_TYPES = {
    # Text/Code
    'txt': 'text/plain',
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',

    # Image
    'gif': 'image/gif',
    'jpg': 'image/jpeg',
    'tiff': 'image/tiff',
    'png': 'image/png',
    'svg': 'image/svg+xml',

    # Data/Document
    'pdf': 'application/pdf',
    'xml': 'text/xml',
    'json': 'application/json',

    # Video
    'mp4': 'video/mp4',
    'm4v': 'video/mp4',
    'ogv': 'video/ogg',
    'flv': 'video/x-flv',
    'webm': 'video/webm',
    '3gp': 'video/3gpp',
    'mpeg': 'video/mpeg',
    'mpg': 'video/mpeg',

    # Audio
    'mp3': 'audio/mpeg',
    'ogg': 'audio/ogg',
    'flac': 'audio/flac',
    'm4a': 'audio/mp4',
    'mpg': 'video/mpeg',

    # Other
    'zip': 'application/zip',
    'gz': 'application/gzip',

}
EXTENSIONS = MIME_TYPES.keys()
DEFAULT_TYPE = MIME_TYPES['txt']
CHARSET = 'UTF-8'
TIMESTAMP_FMT = '%a, %d %b %Y %H:%M:%S GMT'


def get_mimetype(filename):
    """ Guess mime-type based on file's extension

    :param filename:    filename
    """
    name, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext[1:], DEFAULT_TYPE)


def format_ts(seconds=None):
    """ Format timestamp expressed as seconds from epoch in RFC format

    If the ``seconds`` argument is omitted, or is ``None``, the current time is
    used.

    :param seconds:     seconds since local system's epoch
    :returns:           formatted timestamp
    """
    return time.strftime(TIMESTAMP_FMT, time.gmtime(seconds))


def iter_read_range(fd, offset, length, chunksize=1024*1024):
    """ Version of ``bottle._file_iter_range`` that supports zipfile API

    :param fd:          file-like object that may or may not support ``seek()``
    :param offset:      offset from the beginning in bytes
    :param length:      number of bytes to read
    :param chunksize:   maximum size of the chunk
    """
    try:
        fd.seek(offset)
    except AttributeError:
        # this object does not support ``seek()`` so simply discard the first
        # ``offset - 1`` bytes
        fd.read(offset - 1)
    while length > 0:
        chunk = fd.read(min(length, chinksize))
        if not chink:
            break
        length -= len(chunk)
        yield chunk
    fd.close()


def send_file(content, filename, size, timestamp):
    """ Send a file represented by file object

    The code is partly based on ``bottle.static_file``.

    :param content:     file-like object
    :param filename:    filename to use
    :param size:        file size in bytes
    :param timestamp:   file's timestamp seconds since epoch
    """
    headers = {}
    ctype = get_mimetype(filename)

    if ctype.startswith('text/'):
        # We expect and assume all text files are encoded UTF-8. It's
        # broadcaster's job to ensure this is true.
        ctype += '; charset=%s' % CHARSET

    # Set basic headers
    headers['Content-Type'] = ctype
    headers['Content-Length'] = size
    headers['Last-Modified'] = format_ts(timestamp)

    # Check if If-Modified-Since header is in request and respond early if so
    modsince = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    modsince = modsince and parse_date(modsince.split(';')[0].strip())
    if modsince is not None and modsince >= timestamp:
        headers['Date'] = format_ts()
        return HTTPResponse(status=304, **headers)

    if request.method == 'HEAD':
        # Request is a HEAD, so remove any content body
        content = ''


    headers['Accept-Ranges'] = 'bytes'
    ranges = request.environ.get('HTTP_RANGE')
    if ranges:
        ranges = list(parse_range_header(ranges, size))
        if not ranges:
            return HTTPError(416, "Request Range Not Satisfiable")
        start, end = ranges[0]
        headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end - 1, size)
        headers['Content-Length'] = str(end - start)
        content = iter_read_range(content, start, end - start)
    return HTTPResponse(content, **headers)


exists = lambda f: spawn(os.path.exists, f).get()
isfile = lambda f: spawn(os.path.isfile, f).get()
access = lambda f: spawn(os.access, f, os.R_OK).get()


def _file_iter_range(fp, offset, bytes, maxread=1024*1024):
    ''' Yield chunks from a range in a file. No chunk is bigger than maxread.'''
    fp.seek(offset)
    while bytes > 0:
        part = fp.read(min(bytes, maxread))
        if not part: break
        bytes -= len(part)
        yield part
    fp.close()


def _file_iter_all(fp, maxread=1024*1024):
    ''' Yield chnks from a whole file. No chunk is bigger than maxread.'''
    fp.seek(0)
    part = fp.read(maxread)
    while part:
        yield part
        part = fp.read(maxread)
    fp.close()


def gevent_static_file(filename, root, mimetype='auto', download=False,
                       charset='UTF-8'):
    """ Open a file in a safe way and return :exc:`HTTPResponse` with status
        code 200, 305, 403 or 404. The ``Content-Type``, ``Content-Encoding``,
        ``Content-Length`` and ``Last-Modified`` headers are set if possible.
        Special support for ``If-Modified-Since``, ``Range`` and ``HEAD``
        requests.

        :param filename: Name or path of the file to send.
        :param root: Root path for file lookups. Should be an absolute directory
            path.
        :param mimetype: Defines the content-type header (default: guess from
            file extension)
        :param download: If True, ask the browser to open a `Save as...` dialog
            instead of opening the file with the associated program. You can
            specify a custom filename as a string. If not specified, the
            original filename is used (default: False).
        :param charset: The charset to use for files with a ``text/*``
            mime-type. (default: UTF-8)
    """

    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    headers = dict()

    if not filename.startswith(root):
        return HTTPError(403, "Access denied.")
    if not exists(filename) or not isfile(filename):
        return HTTPError(404, "File does not exist.")
    if not access(filename):
        return HTTPError(403, "You do not have permission to access this file.")

    if mimetype == 'auto':
        mimetype, encoding = mimetypes.guess_type(filename)
        if encoding: headers['Content-Encoding'] = encoding

    if mimetype:
        if mimetype[:5] == 'text/' and charset and 'charset' not in mimetype:
            mimetype += '; charset=%s' % charset
        headers['Content-Type'] = mimetype

    if download:
        download = os.path.basename(filename if download == True else download)
        headers['Content-Disposition'] = 'attachment; filename="%s"' % download

    stats = os.stat(filename)
    headers['Content-Length'] = clen = stats.st_size
    lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
    headers['Last-Modified'] = lm

    ims = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if ims:
        ims = parse_date(ims.split(";")[0].strip())
    if ims is not None and ims >= int(stats.st_mtime):
        headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        return HTTPResponse(status=304, **headers)

    body = '' if request.method == 'HEAD' else open(filename, 'rb')

    headers["Accept-Ranges"] = "bytes"
    ranges = request.environ.get('HTTP_RANGE')
    if 'HTTP_RANGE' in request.environ:
        ranges = list(parse_range_header(request.environ['HTTP_RANGE'], clen))
        if not ranges:
            return HTTPError(416, "Requested Range Not Satisfiable")
        offset, end = ranges[0]
        headers["Content-Range"] = "bytes %d-%d/%d" % (offset, end-1, clen)
        headers["Content-Length"] = str(end-offset)
        if body: body = _file_iter_range(body, offset, end-offset)
        return HTTPResponse(body, status=206, **headers)
    return HTTPResponse(_file_iter_all(body) if body else '', **headers)


def patch_static_file():
    import bottle
    bottle.static_file = gevent_static_file
