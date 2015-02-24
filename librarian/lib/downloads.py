"""
downloads.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import glob
import zipfile
import logging
from contextlib import closing
from functools import partial
from datetime import datetime, timedelta

from bottle import request

from .i18n import lazy_gettext as _


__all__ = ('ContentError', 'find_signed', 'is_expired', 'cleanup',
           'get_zipballs', 'get_timestamp', 'get_timestamp_as_datetime',
           'get_md5_from_path', 'get_zip_path_in', 'get_zip_path',
           'remove_downloads', 'get_spool_zip_path', 'get_file',
           'get_metadata', 'patch_html',)


STYLE_LINK = '<link rel="stylesheet" href="/static/css/content.css">'
LICENSES = (
    (None, _('Unknown license')),
    ('CC-BY', _('Creative Commons Attribution')),
    ('CC-BY-ND', _('Creative Commons Attribution-NoDerivs')),
    ('CC-BY-NC', _('Creative Commons Attribution-NonCommercial')),
    ('CC-BY-ND-NC', _('Creative Commons '
                      'Attribution-NonCommercial-NoDerivs')),
    ('CC-BY-SA', _('Creative Commons Attribution-ShareAlike')),
    ('CC-BY-NC-SA', _('Creative Commons '
                      'Attribution-NonCommercial-ShareAlike')),
    ('GFDL', _('GNU Free Documentation License')),
    ('OPL', _('Open Publication License')),
    ('OCL', _('Open Content License')),
    ('ADL', _('Against DRM License')),
    ('FAL', _('Free Art License')),
    ('PD', _('Public Domain')),
    ('OF', _('Other free license')),
    ('ARL', _('All rights reserved')),
    ('ON', _('Other non-free license')),
)


class ContentError(BaseException):
    """ Exception related to content decoding, file extraction, etc """
    def __init__(self, msg, path):
        self.message = msg
        self.path = path
        super(ContentError, self).__init__(msg)


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


def get_zipballs():
    """ Get all zipballs in the spool directory

    :returns:   iterable containing full paths to zipballs
    """
    config = request.app.config
    spooldir = config['content.spooldir']
    output_ext = config['content.output_ext']
    zipfiles = (f for f in os.listdir(spooldir) if f.endswith(output_ext))
    return (os.path.join(spooldir, f) for f in zipfiles)


def order_zipballs(zipballs):
    """ Order zipball paths by timestamp and return timestamps

    :param zipballs:    iterable containing zipballs such as return value of
                        ``get_zipballs`` function
    :returns:           iterable contianing two-tuples of zipballs and their
                        timestamps
    """
    zipdates = [(z, os.stat(z).st_mtime) for z in zipballs]
    return sorted(zipdates, key=lambda x: x[1])


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


def extract_file(path, filename):
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
    try:
        with open(path, 'rb') as f:
            with zipfile.ZipFile(f) as content:
                metadata = content.getinfo(filename)
                content = content.open(filename, 'r').read()
    except zipfile.BadZipfile:
        raise ContentError("'%s' is not a valid zipfile" % path, path)
    except Exception as err:
        raise ContentError("'%s' could not be opened: %s" % (path, err), path)
    return metadata, content


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
    filename = '%s/%s' % (dirname, filename)  # we always use forward slash
    return extract_file(path, filename)


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
        content = str(content.decode('utf-8'))
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
    contentdir = os.path.normpath(config['content.contentdir'])
    return get_zip_path_in(md5, contentdir)


def get_spool_zip_path(md5):
    """ Get zip file path in spool directory from MD5 hash

    :param md5:     md5 of the zipball
    :returns:       actual path to the file of ``None`` if file cannot be found
    """
    config = request.app.config
    spooldir = os.path.normpath(config['content.spooldir'])
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
    :returns:           tuple of new size and HTML bytestring
    """
    html = content.decode('utf8')
    html = html.replace('</head>', STYLE_LINK + '</head>')
    html_bytes = html.encode('utf8')
    size = len(html_bytes)
    return size, html_bytes


class Meta(object):
    """ Metadata wrapper """

    # FIXME: Move this to lib.archive

    IMAGE_EXTENSIONS = ['.png', '.gif', '.jpg', '.jpeg']

    LABEL_TITLES = {
        # Translators, used as label, meaning content belogs to core
        'core': _('core'),
        # Translators, used as label, meaning content was sponsored by someone
        'sponsored': _('sponsored'),
        # Translators, used as label, meaning content is from a partner
        'partner': _('partner')
    }

    def __init__(self, meta):
        self.meta = meta
        self.tags = json.loads(meta.get('tags') or '{}')
        self._image = None

    def __getattr__(self, attr):
        try:
            return self.meta[attr]
        except KeyError:
            raise AttributeError("Attribute or key '%s' not found" % attr)

    def __getitem__(self, key):
        return self.meta[key]

    def __setitem__(self, key, value):
        self.meta[key] = value

    def get(self, key, default=None):
        return self.meta.get(key, default)

    def cache_cover(self, cover_path, content):
        config = request.app.config
        covers = config['content.covers']
        ext = os.path.splitext(cover_path)[1]
        cover_path = os.path.join(covers, '%s.%s' % (self.md5, ext))
        with open(cover_path, 'wb') as f:
            f.write(content)
        return os.path.basename(cover_path)

    def get_cover_path(self):
        config = request.app.config
        covers = config['content.covers']
        cover_path = os.path.join(covers, '%s.*' % self.md5)
        g = glob.glob(cover_path)
        try:
            return os.path.basename(g[0])
        except IndexError:
            return None

    @property
    def label(self):
        if self.archive == 'core':
            return 'core'
        elif self.is_sponsored:
            return 'sponsored'
        elif self.is_partner:
            return 'partner'
        return 'core'

    @property
    def human_label(self):
        return self.LABEL_TITLES[self.label]

    @property
    def free_license(self):
        return self.license not in ['ARL', 'ON']

    @property
    def human_license(self):
        try:
            return dict(LICENSES)[self.license]
        except (KeyError, AttributeError):
            return LICENSES[0][1]

    @property
    def image(self):
        if self._image is not None:
            return self._image
        cover = self.get_cover_path()
        if cover:
            self._image = cover
            return self._image
        zip_path = get_zip_path(self.md5)
        try:
            with open(zip_path, 'rb') as f:
                z = zipfile.ZipFile(f)
                for name in z.namelist():
                    if os.path.splitext(name)[1].lower() in self.IMAGE_EXTENSIONS:
                        self._image = self.cache_cover(name,
                                                       z.open(name, 'r').read())
                        return self._image
        except TypeError:
            # Could not find the zip file
            logging.error("Could not find zip file '%s.zip'" % self.md5)
            return None
