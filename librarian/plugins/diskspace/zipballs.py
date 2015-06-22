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

from ...core.content import to_path, filewalk
from ...lib import squery


def get_database(dbpath):
    """ Return database object given database path

    :param dbpath:  database path
    :returns:       `squery.Database` object
    """
    conn = squery.Database.connect(dbpath)
    return squery.Database(conn)


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
    with db.transaction():
        db.executemany("UPDATE zipballs SET size = ? WHERE md5 = ?", sizes)


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


def free_space(config=None):
    """ Returns free space information about content directory

    :returns:   two-tuple of free space and total space
    """
    config = config or request.app.config
    cdir = config['content.contentdir']
    cdev, cfree, ctot = path_space(cdir)
    return cfree, ctot


def used_space():
    """ Return count of and total space taken by zipballs

    :returns:   two-tuple of zipballs count and space used by them
    """

    db = request.db.main
    q = db.Select(['COUNT(*) AS count', 'SUM(size) AS total'],
                  sets='zipballs')
    db.query(q)
    res = db.results
    return res[0]['count'], res[0]['total'] or 0


def needed_space(free_space, config=None):
    """ Returns the amount of space that needs to be freed, given free space

    :param free_space:  amount of currently available free space (bytes)
    :returns:           amount of additional space that should be freed (bytes)

    """
    config = config or request.app.config
    return max([0, config['storage.minfree'] - free_space])


def get_old_content(db=None):
    """ Return content ordered from oldest to newest

    :returns:   list of content ordered from oldest to newest
    """
    db = db or request.db.main
    db.query("""
             SELECT md5, updated, title, views, tags, archive
             FROM zipballs
             ORDER BY tags IS NULL DESC,
                      views ASC,
                      updated ASC,
                      archive LIKE 'ephem%' DESC;
             """)
    return db.results


def get_content_size(md5, contentdir):
    content_path = os.path.abspath(to_path(md5, prefix=contentdir))
    return sum([os.stat(filepath).st_size
                for filepath in filewalk(content_path)])


def clone_zipball(zipball):
    return dict((key, zipball[key]) for key in zipball.keys())


def cleanup_list(free_space, db=None, config=None):
    """ Return a generator of zipball metadata necessary to free enough space

    The generator will stop yielding as soon as enough zipballs have been
    yielded to satisfy the minimum free space requirement set in the
    configuration.
    """
    # TODO: tests
    zipballs = iter(get_old_content(db=db))
    config = config or request.app.config
    contentdir = config['content.contentdir']
    space = needed_space(free_space, config=config)
    while space > 0:
        zipball = clone_zipball(next(zipballs))
        if 'size' not in zipball:
            zipball['size'] = get_content_size(zipball['md5'], contentdir)

        space -= zipball['size']
        yield zipball
