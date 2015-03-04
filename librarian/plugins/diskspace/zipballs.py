"""
zipballs.py: Tools for dealing with zipballs and their sizes

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging

from bottle import request

from ...lib import squery


FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}


def get_database(dbpath):
    """ Return database object given database path

    :param dbpath:  database path
    :returns:       `squery.Database` object
    """
    return squery.Database(dbpath)


def get_zipballs_without_size(db):
    """ Query the database for any zipballs with unset `size` column

    :param db:  database object
    :returns:   list of hashes
    """
    db.query('SELECT md5 FROM zipballs WHERE size IS NULL')
    return [r['md5'] for r in db.results]


def get_hash_paths(hashes, contentdir):
    """ Return full zipball paths given their hashes

    :param hashes:      list of MD5 hashes
    :param contentdir:  directory containing zipballs
    :returns:           list of hash-path two tuples
    """
    return [(h, os.path.join(contentdir, h + '.zip')) for h in hashes]


def update_rows(hashpaths, db):
    """ Update the size columns of all specified content

    :param hashpaths:   list of hash-path two-tuples
    :param db:          database object
    """
    logging.debug('DISKSPACE: updating size information for %s items',
                  len(hashpaths))
    sizes = ((os.stat(p).st_size, h) for h, p in hashpaths)
    with db.transaction() as cur:
        cur.executemany("UPDATE zipballs SET size = ? WHERE md5 = ?", sizes)


def update_sizes(dbpath, contentdir):
    db = get_database(dbpath)
    hashes = get_zipballs_without_size(db)
    hashpaths = get_hash_paths(hashes, contentdir)
    update_rows(hashpaths, db)


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
    """ Returns free space information about content directory

    :returns:   two-tuple of free space and total space
    """
    config = request.app.config
    cdir = config['content.contentdir']
    cdev, cfree, ctot = path_space(cdir)
    return cfree, ctot


def used_space():
    """ Return count of and total space taken by zipballs

    :returns:   two-tuple of zipballs count and space used by them
    """

    db = request.db
    db.query("""
             SELECT COUNT(*) AS count, SUM(size) AS total
             FROM zipballs;
             """)
    res = db.results
    return res[0]['count'], res[0]['total']


def parse_size(size):
    """ Parses size with B, K, M, or G suffix and returns in size bytes

    :param size:    human-readable size with suffix
    :returns:       size in bytes or 0 if source string is using invalid
                    notation
    """
    size = size.strip().lower()
    if size[-1] not in 'bkmg':
        suffix = 'b'
    else:
        suffix = size[-1]
        size = size[:-1]
    try:
        size = float(size)
    except ValueError:
        return 0
    return size * FACTORS[suffix]


def needed_space(free_space):
    """ Returns the amount of space that needs to be freed, given free space

    :param free_space:  amount of currently available free space (bytes)
    :returns:           amount of additional space that should be freed (bytes)

    """
    config = request.app.config
    return max([0, parse_size(config['storage.minfree']) - free_space])
