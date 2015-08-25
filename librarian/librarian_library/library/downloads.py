"""
downloads.py: Higher-level functions for working with collections of zipballs

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import logging
import os

import scandir

from . import zipballs


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
    filetime = datetime.datetime.fromtimestamp(secs)
    now = datetime.datetime.now()
    return now - filetime >= datetime.timedelta(days=maxage)


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


def get_downloads(spooldir, extension):
    """ Get all zipballs in the spool directory

    :param spooldir:   absolute path to spool directory
    :param extension:  zipball extension
    :returns:          iterable containing full paths to zipballs
    """
    for entry in scandir.scandir(spooldir):
        if entry.name.endswith(extension):
            yield entry.path


def order_downloads(downloads):
    """ Order zipball paths by timestamp and return timestamps

    :param zipballs:  iterable containing zipballs such as return value of
                      ``get_downloads`` function
    :returns:         iterable contianing two-tuples of zipballs and their
                      timestamps
    """
    zipdates = [(z, os.stat(z).st_mtime) for z in downloads]
    return sorted(zipdates, key=lambda x: x[1])


def safe_remove(path):
    """ Remove the specified path, catching and logging if an exception happens

    :param path:  path to remove
    :returns:     boolean indicating success of removal
    """
    if not path:
        return False

    try:
        os.unlink(path)
    except OSError as exc:
        logging.error("Error removing '{0}': '{1}'".format(path, exc))
        return False
    else:
        logging.debug("'{0}' removed.".format(path))
        return True


def remove_downloads(spooldir, extension=None, content_ids=None):
    """ Remove all downloads matching provided content ids

    Removal will fail silently, and will only be logged.

    :param spooldir:     absolute path to spool directory
    :param extension:    zipball extension (mandatory if `md5s` is None)
    :param content_ids:  iterable containing MD5 hexdigests
    :returns:            number of successfully removed downloads
    """
    if not content_ids:
        if not extension:
            raise TypeError('remove_downloads() needs keyword-only argument'
                            ' extension if `content_ids` is not specified.')
        paths = get_downloads(spooldir, extension)
        logging.debug("Removing all items from spool directory")
    else:
        paths = [zipballs.get_zip_path(cid, spooldir) for cid in content_ids]
        msg = "Removing {0} items from spool directory".format(len(paths))
        logging.debug(msg)

    return sum([safe_remove(path) for path in paths])
