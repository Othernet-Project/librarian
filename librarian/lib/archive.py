"""
archive.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import shutil
import logging
from datetime import datetime

from bottle import request

from .downloads import get_spool_zip_path, get_zip_path, get_metadata

from .i18n import lazy_gettext as _


__all__ = ('get_count', 'get_search_count', 'get_content', 'search_content',
           'get_old_content', 'parse_size', 'cleanup_list', 'add_to_archive',
           'remove_from_archive', 'path_space', 'free_space', 'zipball_count',
           'archive_space_used', 'last_update', 'add_view', 'needed_space',
           'cleanup_list')

FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}

LICENSES = (
    (None, _("Unknown license")),
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

COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs;
"""
PAGE_QUERY = """
SELECT *
FROM zipballs
ORDER BY datetime(updated) DESC, views DESC
LIMIT :limit
OFFSET :offset;
"""
SEARCH_COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs
WHERE title LIKE :terms;
"""
SEARCH_QUERY = """
SELECT *
FROM zipballs
WHERE title LIKE :terms
ORDER BY date(updated) DESC, views DESC
LIMIT :limit
OFFSET :offset;
"""
LIST_DELETABLE = """
SELECT md5, updated, title, views
FROM zipballs
WHERE favorite = 0
ORDER BY updated ASC, views ASC;
"""
ADD_QUERY = """
REPLACE INTO zipballs
(md5, domain, url, title, images, timestamp, updated, keep_formatting,
is_partner, is_sponsored, archive, partner, license)
VALUES
(:md5, :domain, :url, :title, :images, :timestamp, :updated, :keep_formatting,
:is_partner, :is_sponsored, :archive, :partner, :license)
"""
REMOVE_QUERY = """
DELETE FROM zipballs
WHERE md5 = ?;
"""
REMOVE_MULTI_QUERY = """
DELETE FROM zipballs
WHERE md5 IN (SEQ);
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
TITLES_QUERY = """
SELECT title, md5
FROM zipballs
WHERE md5 IN (SEQ);
"""


def multiarg(n):
    """ Return ``n`` question marks delimited by comma """
    return ','.join(('? ' * n).strip().split())


def get_count():
    # TODO: tests
    db = request.db
    db.query(COUNT_QUERY)
    return db.cursor.fetchall()[0]['count(*)']


def get_search_count(terms):
    # TODO: tests
    terms = '%' + terms.lower() + '%'
    db = request.db
    db.query(SEARCH_COUNT_QUERY, terms=terms)
    return db.cursor.fetchall()[0]['count']


def get_content(offset=0, limit=0):
    # TODO: tests
    db = request.db
    db.query(PAGE_QUERY, offset=offset, limit=limit)
    return db.cursor.fetchall()


def get_titles(ids):
    q = TITLES_QUERY.replace('SEQ', multiarg(len(ids)))
    db = request.db
    db.query(q, *ids)
    return db.cursor.fetchall()


def get_replacements(metadata):
    replacements = []
    for m in metadata:
        if m.get('replaces') is not None:
            replacements.append(m['replaces'])
    if replacements:
        titles = get_titles(replacements)
    else:
        return []
    titles = {m['md5']: m['title'] for m in titles}
    for m in metadata:
        if m.get('replaces') in titles:
            m['replaces_title'] = titles[m['replaces']]
    return metadata


def search_content(terms, offset=0, limit=0):
    # TODO: tests
    terms = '%' + terms.lower() + '%'
    db = request.db
    db.query(SEARCH_QUERY, terms=terms, offset=offset, limit=limit)
    return db.cursor.fetchall()


def get_old_content():
    # TODO: tests
    db = request.db
    db.query(LIST_DELETABLE)
    return db.cursor.fetchall()


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


def add_to_archive(hashes):
    config = request.app.config
    target_dir = config['content.contentdir']
    db = request.db
    metadata = []
    replaced = []
    copy_list = []
    delete_list = []
    # Prepare data for processing
    for md5, path in ((h, get_spool_zip_path(h)) for h in hashes):
        logging.debug("<%s> adding to archive (#%s)" % (path, md5))
        meta = get_metadata(path)
        meta['md5'] = md5
        meta['updated'] = datetime.now()
        if meta.get('replaces'):
            logging.debug(
                "<%s> replaces '%s'" % (path, meta['replaces']))
            replaced.append(meta['replaces'])
            delete_list.append(get_zip_path(meta['replaces']))
        copy_list.append(path)
        metadata.append(meta)
    # Create replacement query
    nreplaced = len(replaced)
    q = REMOVE_MULTI_QUERY.replace('SEQ', multiarg(nreplaced))
    # Execute database operations
    with db.transaction() as cur:
        logging.debug("Adding new content to archive database")
        cur.executemany(ADD_QUERY, metadata)
        logging.debug("Removing replaced content from archive database")
        cur.execute(q, replaced)
        rowcount = cur.rowcount
    logging.debug("%s items added to database" % rowcount)
    # Delete obsolete content
    for path in delete_list:
        if not path:
            continue
        try:
            os.unlink(path)
        except OSError as err:
            logging.error(
                "<%s> could not delete obsolete file: %s" % (path, err))
    logging.debug("%s items deleted from storage" % len(delete_list))
    # Execute storage operations
    for path in copy_list:
        # Check target path first
        target_path = os.path.join(target_dir, os.path.basename(path))
        if os.path.exists(target_path):
            logging.debug("<%s> removing existing content" % target_path)
            os.unlink(target_path)
        shutil.move(path, target_dir)
    logging.debug("%s items copied to storage" % len(copy_list))
    return rowcount


def remove_from_archive(hashes):
    # TODO: tests
    config = request.app.config
    target_dir = config['content.contentdir']
    db = request.db
    success = []
    failed = []
    for md5, path in ((h, get_zip_path(h)) for h in hashes):
        logging.debug("<%s> removing from archive (#%s)" % (path, md5))
        try:
            os.unlink(path)
        except OSError as err:
            logging.error("<%s> cannot delete: %s" % (path, err))
            failed.append(md5)
            continue
        success.append(md5)
    with db.transaction() as cur:
        logging.debug("Removing %s items from archive database" % len(success))
        cur.executemany(REMOVE_QUERY, [(s,) for s in success])
        rowcount = cur.rowcount
    logging.debug("%s items removed from database" % rowcount)
    return success, failed


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


def get_zip_space(filename, directory=None):
    """ Return space taken up by a file in content directory

    Directory can be overridden by a custom path supplied as ``directory``
    argument. This is useful if we want to prevent multiple lookups of the
    directory path.

    :param filename:    name of the zipfile
    :param directory:   directory of the file
    :returns:           space taken in bytes
    """
    directory = directory or request.app.config['content.contentdir']
    return os.stat(os.path.join(directory, filename)).st_size


def archive_space_used():
    """ Return the space used by zipballs in content directory

    :returns:   used space in bytes
    """
    config = request.app.config
    cdir = config['content.contentdir']
    zipballs = os.listdir(cdir)
    return sum([get_zip_space(f, cdir)
                for f in zipballs
                if f.endswith('.zip')])


def last_update():
    """ Get timestamp of the last updated zipball

    :returns:   datetime object of the last updated zipball
    """
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


def needed_space():
    """ Returns amount of space that needs to be freed in content directory

    :returns:   space in bytes
    """
    # TODO: tests
    config = request.app.config
    return max([0, parse_size(config['storage.minfree']) - free_space()[1][0]])


def cleanup_list():
    """ Return a generator of zipball metadata necessary to free enough space

    The generator will stop yielding as soon as enough zipballs have been
    yielded to satisfy the minimum free space requirement set in the
    configuration.
    """
    # TODO: tests
    old = get_old_content()
    config = request.app.config
    cdir = config['content.contentdir']
    zspace = lambda z: get_zip_space(z['md5'] + '.zip', cdir)
    zipballs = map(lambda z: (z.setdefault('size', zspace(z)) and z), old)
    space = needed_space()
    while space > 0:
        zipball = next(zipballs)
        space -= zipball['size']
        yield zipball


