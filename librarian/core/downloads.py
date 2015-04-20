"""
downloads.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import zipfile
import logging
from datetime import datetime, timedelta

from .metadata import convert_json, DecodeError, FormatError


class ContentError(BaseException):
    """ Exception related to content decoding, file extraction, etc """
    def __init__(self, msg, path):
        self.message = msg
        self.path = path
        super(ContentError, self).__init__(msg)


def find_signed(spooldir, extension):
    """ Find all signed files in the spool directory

    :param spooldir:    absolute path to spool directory
    :param extension:   extension of signed files
    :returns:   iterator containing all filtered items
    """
    everything = os.listdir(spooldir)
    everything = (f for f in everything if f.endswith('.' + extension))
    return (os.path.join(spooldir, f) for f in everything)


def is_expired(secs, maxage):
    """ Checks if timestamp has expired according to keep option

    :param secs:    seconds from epoch of the local system
    :param maxage:  maximum allowed lifetime in days
    :returns:       whether file has expired
    """
    filetime = datetime.fromtimestamp(secs)
    now = datetime.now()
    return now - filetime >= timedelta(days=maxage)


def cleanup(files, maxage):
    """ Remove obsolete signed files

    Cleanup is done based on the passed in maxage param and files' timestamps.

    This function simply assume all files exist and are accessible, so
    ``OSError`` and similar exceptions are not trapped. It is the user's
    responsibility to make sure files do exist.

    :param files:   list of file paths
    :param maxage:  maximum allowed lifetime of files in days
    :returns:       list of files that were kept
    """
    kept = []
    logging.debug("Cleaning up spool directory")
    for path in files:
        if is_expired(os.path.getmtime(path), maxage):
            logging.debug("Removing expired file '%s'" % path)
            os.unlink(path)
        else:
            kept.append(path)
    logging.debug("Cleanup complete, %s files kept" % len(kept))
    return kept


def get_zipballs(spooldir, extension):
    """ Get all zipballs in the spool directory

    :param spooldir:    absolute path to spool directory
    :param extension:   zipball extension
    :returns:   iterable containing full paths to zipballs
    """
    zipfiles = (f for f in os.listdir(spooldir) if f.endswith(extension))
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


def extract_file(path, filename, no_read=False):
    """ Extract a single file from a zipball into memory

    This function is cached using in-memory cache with arguments as keys.

    You can read more about the caching in Python documentation.

    https://docs.python.org/3/library/functools.html#functools.lru_cache

    :param path:        path to the zip file
    :param filename:    name of the file to extract
    :param no_read:     return file handle instead of file contents
    :returns:           two-tuple in ``(metadata, content)`` format, containing
                        ``zipfile.ZipInfo`` object and file content
                        respectively
    """
    try:
        # Note that we do NOT close the file handle if ``no_read`` is used.
        # This is intentional. If file handle is closed, the file handle we
        # return will be no good to the caller.
        f = open(path, 'rb')
        content = zipfile.ZipFile(f)
        metadata = content.getinfo(filename)
        fd = content.open(filename, 'r')
        if no_read:
            # We are retruning the file descriptor pointing to the zipfile
            # contents. This is not a real file descritor, just a file-like
            # object (it has read() but not seek().
            content = fd
        else:
            content = fd.read()
            fd.close()
            f.close()  # We've read the content, so it's safe to close
    except zipfile.BadZipfile:
        raise ContentError("'%s' is not a valid zipfile" % path, path)
    except Exception as err:
        raise ContentError("'%s' could not be opened: %s" % (path, err), path)
    return metadata, content


def get_file(path, filename, no_read=False):
    """ Extract a single file from a zipball into memory

    This function is cached using in-memory cache with arguments as keys.

    You can read more about the caching in Python documentation.

    https://docs.python.org/3/library/functools.html#functools.lru_cache

    :param path:        path to the zip file
    :param filename:    name of the file to extract
    :param no_read:     return file handle instead of file contents
    :returns:           two-tuple in ``(metadata, content)`` format, containing
                        ``zipfile.ZipInfo`` object and file content
                        respectively
    """
    # TODO: Add caching
    dirname = get_md5_from_path(path)
    filename = '%s/%s' % (dirname, filename)  # we always use forward slash
    return extract_file(path, filename, no_read)


def get_metadata(path, meta_filename):
    """ Extract metadata file from zipball and return its content

    The extraction happens in-memory, so no files are written out. Files
    without metadata will be treated as bad files, but will not be
    automatically removed. Decision to remove such files is left to the user.

    :param path:    path to the zip file
    :returns:       metadata dict
    """
    metadata, content = get_file(path, meta_filename)
    try:
        return convert_json(content)
    except DecodeError as err:
        raise ContentError("Failed to decode metadata: '%s'" % err)
    except FormatError:
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


def get_zip_path(md5, contentdir):
    """ Get zip file path from MD5 hash

    :param md5:          md5 of the zipball
    :param contentdir:   absolute path to the folder of zipballs
    :returns:       actual path to the file or `None` if file cannot be found
    """
    return get_zip_path_in(md5, os.path.normpath(contentdir))


def get_spool_zip_path(md5, spooldir):
    """ Get zip file path in spool directory from MD5 hash

    :param md5:       md5 of the zipball
    :param spooldir:  absolute path to spool directory
    :returns:         actual path to the file or `None` if file cannot be found
    """
    return get_zip_path_in(md5, os.path.normpath(spooldir))


def remove_downloads(spooldir, extension=None, md5s=None):
    """ Remove all downloads matching provided MD5 hexdigests

    Removal will fail silently. No exceptions are raised and no errors are
    returned from this function. The user is expected to either ignore error
    conditions or check for removal themselves.

    :param spooldir:   absolute path to spool directory
    :param extension:  zipball extension (mandatory if `md5s` is None)
    :param md5s:       iterable containing MD5 hexdigests
    """
    if not md5s:
        if not extension:
            raise TypeError('remove_downloads() needs keyword-only argument'
                            ' extension if `md5s` is not specified.')
        paths = get_zipballs(spooldir, extension)
        logging.debug("Removing all items from spool directory")
    else:
        paths = (get_spool_zip_path(md5, spooldir) for md5 in md5s)
        logging.debug("Removing %s items from spool directory" % len(md5s))
    for path in paths:
        if not path:
            logging.debug("<%s> not found on disk" % path)
            continue  # Ignoring non-existent paths
        try:
            os.unlink(path)
            logging.debug("<%s> removed" % path)
        except OSError as err:
            logging.error("<%s> cound not remove: %s" % (path, err))
