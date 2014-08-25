"""
downloads.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import zipfile
import logging
from io import BytesIO
from contextlib import closing
from functools import partial
from datetime import datetime, timedelta

from bottle import request

from .content_crypto import extract_content, DecryptionError


__all__ = ('ContentError', 'find_signed', 'is_expired', 'cleanup',
           'get_decryptable', 'decrypt_all', 'get_zipballs', 'get_timestamp',
           'get_timestamp_as_datetime', 'get_md5_from_path', 'get_zip_path_in',
           'get_zip_path', 'remove_downloads', 'get_spool_zip_path',
           'get_file', 'get_metadata', 'patch_html',)


STYLE_LINK = '<link rel="stylesheet" href="/static/css/content.css">'


class ContentError(BaseException):
    """ Exception related to content decoding, file extraction, etc """
    def __init__(self, msg, path):
        self.message = msg
        self.path = path
        super().__init__(msg)


def find_signed():
    """ Find all signed files in the spool directory

    :returns:   iterator containing all filtered items
    """
    config = request.app.config
    spooldir = config['content.spooldir']
    extension = config['content.extension']
    everything = os.listdir(spooldir)
    everything = (f for f in everything if f.endswith('.' + extension))
    return (os.path.join(spooldir, f) for f in everything)


def is_expired(secs):
    """ Checks if timestamp has expired according to keep option

    :param secs:    seconds from epoch of the local system
    :returns:       whether file has expired
    """
    config = request.app.config
    maxage = timedelta(days=int(config['content.keep']))
    filetime = datetime.fromtimestamp(secs)
    now = datetime.now()
    return now - filetime >= maxage


def cleanup(files):
    """ Remove obsolete signed files

    Cleanup is done based on ``'content.keep'`` setting and files' timestamps.

    This function simply assume all files exist and are accessible, so
    ``OSError`` and similar exceptions are not trapped. It is the user's
    responsibility to make sure files do exist.

    :param files:   list of file paths
    :returns:       list of files that were kept
    """
    kept = []
    logging.debug("Cleaning up spool directory")
    for path in files:
        if is_expired(os.path.getmtime(path)):
            logging.debug("Removing expired file '%s'" % path)
            os.unlink(path)
        else:
            kept.append(path)
    logging.debug("Cleanup complete, %s files kept" % len(kept))
    return kept


def get_decryptable():
    """ Return an iterable of extractable files

    :returns:   iterable containing files that can be decrypted
    """
    return cleanup(find_signed())


def decrypt_all(signed):
    """ Extract all signed files into zip files and remove the originals

    The function will try to extract each of the signed files in the spool
    directory, and compiled a list of extracted zipballs and list of extraction
    errors, and return them as a two-tuple.

    Original signed files that are successfully extracted are removed.

    :param signed:  iterable containing paths to be decrypted
    :returns:       tuple ``(extracted, errors)`` where ``extracted`` is a list
                    of paths of extracted zipballs, and ``errors`` is a list of
                    error objects for each failed extraction.
    """
    config = request.app.config
    extract = partial(extract_content, keyring=config['content.keyring'],
                      output_dir=config['content.spooldir'],
                      output_ext=config['content.output_ext'])
    extracted = []
    errors = []

    for signedf in signed:
        logging.debug("<%s> verifying" % signedf)
        try:
            # TODO: Check space before continuing
            zipball = extract(signedf)
        except DecryptionError as err:
            logging.error("<%s> could not decrypt: %s" % (
                signedf, err))
            errors.append(err)
            continue
        # TODO: Add test for this branching
        if zipfile.is_zipfile(zipball):
            # This seems to be a zip file, so we can include it in the list of
            # extracted files and remove the signed source
            extracted.append(zipball)
            os.unlink(signedf)
            logging.info("<%s> verified" % zipball)
        else:
            # Zipball is invalid. We will leave the signed source alone (maybe
            # it was not downloaded correctly and will be re-downloaded), and
            # remove the zipball.
            logging.error("<%s> invalid zip file" % zipball)
            errors.append(signedf)
            os.unlink(zipball)
    return extracted, errors


def get_zipballs():
    """ Get all zipballs in the spool directory

    :returns:   iterable containing full paths to zipballs
    """
    config = request.app.config
    spooldir = config['content.spooldir']
    output_ext = config['content.output_ext']
    zipfiles = (f for f in os.listdir(spooldir) if f.endswith(output_ext))
    return (os.path.join(spooldir, f) for f in zipfiles)


def get_timestamp(path):
    """ Get the timestamp of a file

    For archived zipballs, this is usually the time when zipball was added to
    the archive.

    :param path:    path to the file
    :returns:       seconds since epoch
    """
    return os.stat(path).st_mtime


def get_timestamp_as_datetime(path):
    """ Get timestamp of a file as datetime object

    For archived zipballs, this is usually the time when zipball was written to
    disk.

    :param path:    path to the file
    :returns:       datetime object
    """
    ts = get_timestamp(path)
    return datetime.fromtimestamp(ts)


def get_md5_from_path(path):
    """ Return MD5 hash from the filename

    This function will actually work with any path, not just ones that contain
    md5. It doesn't really check if the path contains valid md5 hexdigest.

    The function really returns the path without directory tree and extension
    portions.

    :param path:    path to signed file or zipball
    :returns:       md5 portion of the filename
    """
    return os.path.basename(os.path.splitext(path)[0])


def get_file(path, filename):
    """ Extract a single file from a zipball into memory

    This function is cached using in-memory cache with arguments as keys.

    You can read more about the caching in Python documentation.

    https://docs.python.org/3/library/functools.html#functools.lru_cache

    :param path:        path to the zip file
    :param filename:    name of the file to extract
    :returns:           two-tuple in ``(metadata, content)`` format, containing
                        ``zipfile.ZipInfo`` object and file content
                        respectively
    """
    # TODO: Add caching
    dirname = get_md5_from_path(path)
    filename = os.path.join(dirname, filename)
    if not zipfile.is_zipfile(path):
        raise ContentError("'%s' is not a valid zipball" % path, path)
    with closing(zipfile.ZipFile(path, 'r')) as content:
        metadata = content.getinfo(filename)
        content = content.open(filename, 'r')
    return metadata, content


def get_metadata(path):
    """ Extract metadata file from zipball and return its content

    The extraction happens in-memory, so no files are written out. Files
    without metadata will be treated as bad files, but will not be
    automatically removed. Decision to remove such files is left to the user.

    :param path:    path to the zip file
    :returns:       metadata dict
    """
    config = request.app.config
    meta_filename = config['content.metadata']
    metadata, content = get_file(path, meta_filename)
    try:
        content = str(content.read().decode('utf-8'))
    except UnicodeDecodeError as err:
        raise ContentError("Failed to decode metadata: '%s'" % err)
    try:
        return json.loads(content)
    except ValueError as err:
        raise ContentError("Bad metadata for '%s'" % path, path)


def get_zip_path_in(md5, directory):
    """ Return zip path in a directory

    :param md5:         MD5 hex of the zipball
    :param directory:   directory in which to look for files
    """
    filepath = os.path.join(directory, md5 + '.zip')
    if os.path.exists(filepath):
        return filepath
    return None


def get_zip_path(md5):
    """ Get zip file path from MD5 hash

    :param md5:     md5 of the zipball
    :returns:       actual path to the file of ``None`` if file cannot be found
    """
    config = request.app.config
    contentdir = config['content.contentdir']
    return get_zip_path_in(md5, contentdir)


def get_spool_zip_path(md5):
    """ Get zip file path in spool directory from MD5 hash

    :param md5:     md5 of the zipball
    :returns:       actual path to the file of ``None`` if file cannot be found
    """
    config = request.app.config
    spooldir = config['content.spooldir']
    return get_zip_path_in(md5, spooldir)


def remove_downloads(md5s):
    """ Remove all downloads matching provided MD5 hexdigests

    Removal will fail silently. No exceptions are raised and no errors are
    returned from this function. The user is expected to either ignore error
    conditions or check for removal themselves.

    :param md5s:    iterable containing MD5 hexdigests
    """
    logging.debug("Removing %s items from spool directory" % len(md5s))
    for md5 in md5s:
        path = get_spool_zip_path(md5)
        if not path:
            logging.debug("<%s> not found on disk" % path)
            continue  # Ignoring non-existent paths
        try:
            os.unlink(path)
            logging.debug("<%s> removed" % path)
        except OSError as err:
            logging.error("<%s> cound not remove: %s" % (path, err))


def patch_html(content):
    """ Patches HTML and adds a link tag for stylesheet

    :param content:     file-like object
    :returns:           tuple of new size and BytesIO object
    """
    html = content.read().decode('utf8')
    html = html.replace('</head>', STYLE_LINK + '</head>')
    html_bytes = bytes(html, encoding='utf8')
    size = len(html_bytes)
    return size, BytesIO(html_bytes)

