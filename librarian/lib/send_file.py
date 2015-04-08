"""
send_file.py: functions for sending static files

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import time

from bottle import (HTTPResponse, HTTPError, parse_date, parse_range_header,
                    request)


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


class FileRangeWrapper(object):
    """ Wrapper around file-like object to provide reading within range

    This class is specifically crafted to take advantage of
    ``wsgi.file_wrapper`` feature which is available in some WSGI wervers. The
    class mimics the file objects and internally adjusts the reads for a
    specified range.
    """
    def __init__(self, fd, offset, length):
        self.fd = fd
        self.offset = offset
        self.remaining = length
        if offset:
            try:
                self.fd.seek(offset)
            except AttributeError:
                # File handles for zip file content have no seek() so we simply
                # read and discard the data immediately.
                self.fd.read(offset)

    def read(self, size=None):
        if not self.fd:
            raise ValueError('I/O on closed file')
        if not size:
            size = self.remaining
        size = min([self.remaining, size])
        if not size:
            return ''
        data = self.fd.read(size)
        self.remaining -= size
        return data

    def close(self):
        self.fd.close()
        self.fd = None


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


def send_file(fd, filename, size, timestamp):
    """ Send a file represented by file object

    The code is partly based on ``bottle.static_file``.

    :param fd:          file-like object
    :param filename:    filename to use
    :param size:        file size in bytes
    :param timestamp:   file's timestamp seconds since epoch
    """
    assert hasattr(fd, 'read'), 'Expected fd to be file-like object'
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
        # Request is a HEAD, so remove any fd body
        fd = ''

    headers['Accept-Ranges'] = 'bytes'
    ranges = request.environ.get('HTTP_RANGE')
    if ranges:
        ranges = list(parse_range_header(ranges, size))
        if not ranges:
            return HTTPError(416, "Request Range Not Satisfiable")
        start, end = ranges[0]
        headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end - 1, size)
        headers['Content-Length'] = str(end - start)
        fd = FileRangeWrapper(fd, start, end - start)
    return HTTPResponse(fd, **headers)
