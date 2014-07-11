"""
downloads.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import shutil
import zipfile
from io import BytesIO
from contextlib import closing
from functools import partial
from datetime import datetime, timedelta

from bottle import request

from .content_crypto import extract_content, DecryptionError
from . import __version__ as _version, __author__ as _author


__version__ = _version
__author__ = _author
__all__ = ('ContentError', 'find_signed', 'is_expired', 'cleanup',
           'get_decryptable', 'decrypt_all', 'get_zipballs', 'get_timestamp',
           'get_md5_from_path', 'get_zip_path_in', 'get_zip_path',
           'remove_downloads', 'get_spool_zip_path', 'get_file',
           'get_metadata', 'add_to_archive', 'patch_html', 'path_space',
           'free_space', 'zipball_count', 'archive_space_used',
           'favorite_content', 'mark_favorite', 'last_update')

ADD_QUERY = """
REPLACE INTO zipballs
(md5, domain, url, title, images, timestamp, updated)
VALUES
(:md5, :domain, :url, :title, :images, :timestamp, :updated)
"""
COUNT_QUERY = "SELECT count(*) FROM zipballs;"
FAVS_QUERY = """
SELECT * FROM zipballs
WHERE favorite = 1
ORDER BY views DESC, updated DESC;
"""
MARK_FAV_QUERY = "UPDATE zipballs SET favorite = :fav WHERE md5 = :md5;"
LAST_DATE_QUERY = "SELECT updated FROM zipballs ORDER BY updated DESC LIMIT 1"
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
    now = datetime.now()
    kept = []
    for path in files:
        if is_expired(os.path.getmtime(path)):
            os.unlink(path)
        else:
            kept.append(path)
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
        try:
            extracted.append(extract(signedf))
        except DecryptionError as err:
            errors.append(err)
            continue
        os.unlink(signedf)
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
    for md5 in md5s:
        path = get_spool_zip_path(md5)
        if not path:
            continue  # Ignoring non-existent paths
        try:
            os.unlink(path)
        except OSError:
            pass  # Intentionally ignoring. Not considered critical.


def add_to_archive(hashes):
    config = request.app.config
    target_dir = config['content.contentdir']
    db = request.db
    metadata = []
    for md5, path in [(h, get_spool_zip_path(h)) for h in hashes]:
        meta = get_metadata(path)
        meta['md5'] = md5
        meta['updated'] = datetime.now()
        shutil.move(path, target_dir)
        metadata.append(meta)
    with db.transaction() as cur:
        cur.executemany(ADD_QUERY, metadata)
        rowcount = cur.rowcount
    return rowcount


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


def path_space(path):
    """ Return device number and free space in bytes for given path

    :param path:    path for which to return the data
    :returns:       three-tuple containing drive number, free space, total
                    space
    """
    dev = os.stat(path).st_dev
    stat = os.statvfs(path)
    free = stat.f_frsize * stat.f_bavail
    total = stat.f_blocks * stat.f_frsize
    return dev, free, total


def free_space():
    """ Returns free space information about spool and content dirs and totals

    In case the spool directory and content directory are on the same drive,
    the space information is the same for both directories and totals.

    :returns:   three-tuple of two-tuples containing free and total spaces for
                spool directory, content directory, and totals respectively
    """
    config = request.app.config
    sdir = config['content.spooldir']
    cdir = config['content.contentdir']
    sdev, sfree, stot = path_space(sdir)
    cdev, cfree, ctot = path_space(cdir)
    if sdev == cdev:
        total_free = sfree
        total = stot
    else:
        total_free = sfree + cfree
        total = stot + ctot
    return (sfree, stot), (cfree, ctot), (total_free, total)


def zipball_count():
    """ Return the count of zipballs in archive

    :returns:   integer count
    """
    db = request.db
    db.query(COUNT_QUERY)
    return db.cursor.fetchone()['count(*)']


def archive_space_used():
    """ Return the space used by zipballs in content directory

    :returns:   used space in bytes
    """
    config = request.app.config
    cdir = config['content.contentdir']
    zipballs = os.listdir(cdir)
    return sum([os.stat(os.path.join(cdir, f)).st_size
                for f in zipballs
                if f.endswith('.zip')])


def favorite_content(limit=None):
    """ Query database for favorited content

    :param limit:   optional limit on number of items to fetch
    :returns:       iterable of dbdict objects
    """
    # TODO: Unit tests
    db = request.db
    if limit:
        db.query(FAVS_QUERY.strip(';\n ') + ' LIMIT ?;', limit)
    else:
        db.query(FAVS_QUERY)
    return db.cursor.fetchall()


def mark_favorite(md5, val=1):
    """ Mark archive record with MD5 key as favorite

    :param md5:     primary key of the record
    :param val:     favorite value, set it to 1 for favorite, 0 for unfavorite
    :returns:       ``True`` if update was successful, ``False`` otherwise
    """
    # TODO: Unit tests
    db = request.db
    db.query(MARK_FAV_QUERY, fav=val, md5=md5)
    db.commit()
    return db.cursor.rowcount == 1


def last_update():
    """ Get timestamp of the last updated zipball

    :returns:   datetime object of the last updated zipball
    """
    # TODO: Unit tests
    db = request.db
    db.query(LAST_DATE_QUERY)
    res = db.cursor.fetchone()
    return res and res.updated

