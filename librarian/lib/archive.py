"""
archive.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import shutil
from datetime import datetime

from bottle import request

from .downloads import get_spool_zip_path, get_metadata


__all__ = ('get_content', 'add_to_archive', 'path_space', 'free_space',
           'zipball_count', 'archive_space_used', 'last_update',)


LIST_QUERY = """
SELECT *
FROM zipballs
ORDER BY date(updated) DESC, views DESC;
"""
ADD_QUERY = """
REPLACE INTO zipballs
(md5, domain, url, title, images, timestamp, updated)
VALUES
(:md5, :domain, :url, :title, :images, :timestamp, :updated)
"""
COUNT_QUERY = """
SELECT count(*)
FROM zipballs;
"""
LAST_DATE_QUERY = """
SELECT updated
FROM zipballs
ORDER BY updated DESC
LIMIT 1;
"""
VIEWCOUNT_QUERY = """
UPDATE zipballs
SET views = views + 1
WHERE md5 = ?
"""


def get_content():
    db = request.db
    db.query(LIST_QUERY)
    return db.cursor.fetchall()


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


def zipball_count():
    """ Return the count of zipballs in archive

    :returns:   integer count
    """
    db = request.db
    db.query(COUNT_QUERY)
    return db.cursor.fetchone()['count(*)']


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


def last_update():
    """ Get timestamp of the last updated zipball

    :returns:   datetime object of the last updated zipball
    """
    # TODO: Unit tests
    db = request.db
    db.query(LAST_DATE_QUERY)
    res = db.cursor.fetchone()
    return res and res.updated


def add_view(md5):
    """ Increments the viewcount for zipball with specified MD5

    :param md5:     MD5 of the zipball
    :returns:       ``True`` if successful, ``False`` otherwise
    """
    db = request.db
    db.query(VIEWCOUNT_QUERY, md5)
    db.commit()
    return db.cursor.rowcount

