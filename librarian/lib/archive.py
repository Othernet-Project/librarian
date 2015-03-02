"""
archive.py: Download handling

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import shutil
import logging
from functools import wraps
from datetime import datetime

from bottle import request, abort

from .downloads import (
    get_spool_zip_path, get_zip_path, get_metadata, LICENSES, Meta)

from .i18n import lazy_gettext as _

FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}

METADATA_KEYS = (
    'domain', 'url', 'title', 'images', 'timestamp', 'keep_formatting',
    'is_partner', 'is_sponsored', 'archive', 'partner', 'license')

COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs;
"""
TAG_COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs NATURAL JOIN taggings
WHERE tag_id = ?;
"""
PAGE_QUERY = """
SELECT *
FROM zipballs
ORDER BY datetime(updated) DESC, views DESC
LIMIT :limit
OFFSET :offset;
"""
TAG_PAGE_QUERY = """
SELECT *
FROM zipballs NATURAL JOIN taggings
WHERE tag_id = :tag_id
ORDER BY datetime(updated) DESC, views DESC
LIMIT :limit
OFFSET :offset;
"""
SEARCH_COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs
WHERE title LIKE :terms;
"""
TAG_SEARCH_COUNT_QUERY = """
SELECT COUNT(*) AS count
FROM zipballs NATURAL JOIN taggings
WHERE title LIKE :terms AND tag_id = :tag_id;
"""
SEARCH_QUERY = """
SELECT *
FROM zipballs
WHERE title LIKE :terms
ORDER BY date(updated) DESC, views DESC
LIMIT :limit
OFFSET :offset;
"""
TAG_SEARCH_QUERY = """
SELECT *
FROM zipballs NATURAL JOIN taggings
WHERE title LIKE :terms AND tag_id = :tag_id
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
:is_partner, :is_sponsored, :archive, :partner, :license);
"""
REMOVE_QUERY = """
DELETE FROM zipballs
WHERE md5 = ?;
"""
REMOVE_MULTI_QUERY = """
DELETE FROM zipballs
WHERE md5 IN (??);
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
WHERE md5 = ?;
"""
TITLES_QUERY = """
SELECT title, md5
FROM zipballs
WHERE md5 IN (??);
"""
GET_SINGLE = """
SELECT *
FROM zipballs
WHERE md5 = ?;
"""
GET_TAGS = """
SELECT *
FROM tags;
"""
GET_TAG_BY_ID = """
SELECT name
FROM tags
WHERE tag_id = ?;
"""
GET_CONTENT_TAGS = """
SELECT tags.*
FROM tags NATURAL JOIN taggings
WHERE taggings.md5 = ?;
"""
GET_TAG_CONTENTS = """
SELECT zipballs.*
FROM zipballs NATURAL JOIN taggings
WHERE taggings.tag_id IN (??);
"""
GET_TAGS_BY_NAME = """
SELECT *
FROM tags
WHERE name IN (??);
"""
CREATE_TAGS = """
INSERT INTO tags
(name)
VALUES
(:name);
"""
ADD_TAGS = """
INSERT INTO taggings
(tag_id, md5)
VALUES
(:tag_id, :md5);
"""
REMOVE_TAGS = """
DELETE
FROM taggings
WHERE md5 = ? AND tag_id IN (??);
"""
REMOVE_ALL_TAGS = """
DELETE FROM taggings
WHERE md5 = ?;
"""
CACHE_TAGS = """
UPDATE zipballs
SET tags = :tags
WHERE md5 = :md5;
"""
GET_TAG_CLOUD = """
SELECT name, tag_id, count(taggings.tag_id) as count
FROM tags NATURAL JOIN taggings
GROUP BY taggings.tag_id
ORDER BY name ASC;
"""


def add_missing_keys(meta):
    """ Make sure metadata contains all required keys """
    for key in METADATA_KEYS:
        if key not in meta:
            meta[key] = None


def multiarg(query, n):
    """ Returns version of query where '??' is replaced by n placeholders """
    return query.replace('??', ', '.join('?' * n))


def get_count(tag=None):
    # TODO: tests
    db = request.db
    if tag:
        db.query(TAG_COUNT_QUERY, tag)
    else:
        db.query(COUNT_QUERY)
    return db.results[0]['count']


def get_search_count(terms, tag=None):
    # TODO: tests
    terms = '%' + terms.lower() + '%'
    db = request.db
    if tag:
        db.query(TAG_SEARCH_COUNT_QUERY, terms=terms, tag_id=tag)
    else:
        db.query(SEARCH_COUNT_QUERY, terms=terms)
    return db.results[0]['count']


def get_content(offset=0, limit=0, tag=None):
    # TODO: tests
    db = request.db
    if tag:
        db.query(TAG_PAGE_QUERY, offset=offset, limit=limit, tag_id=tag)
    else:
        db.query(PAGE_QUERY, offset=offset, limit=limit)
    return db.results


def get_single(md5):
    # TODO: tests
    db = request.db
    db.query(GET_SINGLE, md5)
    return db.results[0]


def get_titles(ids):
    q = multiarg(TITLES_QUERY, len(ids))
    db = request.db
    db.query(q, *ids)
    return db.results


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


def search_content(terms, offset=0, limit=0, tag=None):
    # TODO: tests
    terms = '%' + terms.lower() + '%'
    db = request.db
    if tag:
        db.query(TAG_SEARCH_QUERY, terms=terms, offset=offset, limit=limit,
                 tag_id=tag)
    else:
        db.query(SEARCH_QUERY, terms=terms, offset=offset, limit=limit)
    return db.results


def get_old_content():
    # TODO: tests
    db = request.db
    db.query(LIST_DELETABLE)
    return db.results


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


def prepare_metadata(md5, path):
    meta = get_metadata(path)
    add_missing_keys(meta)
    meta['md5'] = md5
    meta['updated'] = datetime.now()
    return meta


def add_meta_to_db(db, metadata, replaced):
    nreplaced = len(replaced)
    q = multiarg(REMOVE_MULTI_QUERY, nreplaced)
    with db.transaction() as cur:
        logging.debug("Adding new content to archive database")
        cur.executemany(ADD_QUERY, metadata)
        rowcount = cur.rowcount
        logging.debug("Removing replaced content from archive database")
        cur.execute(q, replaced)
    return rowcount


def delete_obsolete(obsolete):
    for path in obsolete:
        if not path:
            continue
        try:
            os.unlink(path)
        except OSError as err:
            logging.error(
                "<%s> could not delete obsolete file: %s" % (path, err))


def copy_to_archive(paths, target_dir):
    for path in paths:
        target_path = os.path.join(target_dir, os.path.basename(path))
        if os.path.exists(target_path):
            logging.debug("<%s> removing existing content" % target_path)
            os.unlink(target_path)
        shutil.move(path, target_dir)


def process_content_files(content):
    to_add = []
    to_replace = []
    to_copy = []
    to_delete = []
    # Prepare data for processing
    for md5, path in content:
        if not path:
            logging.debug("skipping '%s', file not found", md5)
            continue
        logging.debug("<%s> adding to archive (#%s)" % (path, md5))
        meta = prepare_metadata(md5, path)
        if meta.get('replaces'):
            logging.debug(
                "<%s> replaces '%s'" % (path, meta['replaces']))
            to_replace.append(meta['replaces'])
            to_delete.append(get_zip_path(meta['replaces']))
        to_copy.append(path)
        to_add.append(meta)
    return to_add, to_replace, to_delete, to_copy


def process_content(db, to_add, to_replace, to_delete, to_copy):
    content_dir = request.app.config['content.contentdir']
    rowcount = add_meta_to_db(db, to_add, to_replace)
    delete_obsolete(to_delete)
    copy_to_archive(to_copy, content_dir)
    return rowcount


def process(db, content, no_file_ops=False):
    to_add, to_replace, to_delete, to_copy = process_content_files(content)
    if no_file_ops:
        to_delete = []
        to_copy = []
    rows = process_content(db, to_add, to_replace, to_delete, to_copy)
    return rows, len(to_delete), len(to_copy)


def add_to_archive(hashes):
    db = request.db
    content = ((h, get_spool_zip_path(h)) for h in hashes)
    rows, deleted, copied = process(db, content)
    logging.debug("%s items added to database", rows)
    logging.debug("%s items deleted from storage", deleted)
    logging.debug("%s items copied to storage", copied)
    return rows


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
        cur.executemany(REMOVE_ALL_TAGS, [(s,) for s in success])
        rowcount = cur.rowcount
    logging.debug("%s items removed from database" % rowcount)
    return success, failed


def zipball_count():
    """ Return the count of zipballs in archive

    :returns:   integer count
    """
    db = request.db
    db.query(COUNT_QUERY)
    return db.cursor.fetchone()['count']


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
    if not hasattr(os, 'statvfs'):
        return (None, None), (None, None), (None, None)
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
    if not hasattr(os, 'statvfs'):
        return None
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


def add_tags(meta, tags):
    """ Take content data and comma-separated tags and add the taggings """
    if not tags:
        return
    db = request.db

    # First ensure all tags exist
    with db.transaction() as cur:
        cur.executemany(CREATE_TAGS, [{'name': t} for t in tags])

    # Get the IDs of the tags
    db.query(multiarg(GET_TAGS_BY_NAME, len(tags)), *tags)
    tags = db.results
    ids = [i['tag_id'] for i in tags]

    # Create taggings
    pairs = [{'md5': meta.md5, 'tag_id': i} for i in ids]
    print(pairs)
    tags_dict = {t['name']: t['tag_id'] for t in tags}
    meta.tags.update(tags_dict)
    with db.transaction() as cur:
        cur.executemany(ADD_TAGS, pairs)
        cur.execute(CACHE_TAGS, dict(md5=meta.md5, tags=json.dumps(meta.tags)))
    return tags


def remove_tags(meta, tags):
    """ Take content data nad comma-separated tags and removed the taggings """
    if not tags:
        return
    tag_ids = [meta.tags[name] for name in tags]
    meta.tags = dict((n, i) for n, i in meta.tags.items() if n not in tags)
    db = request.db
    with db.transaction() as cur:
        cur.execute(multiarg(REMOVE_TAGS, len(tag_ids)), [meta.md5] + tag_ids)
        cur.execute(CACHE_TAGS, dict(md5=meta.md5, tags=json.dumps(meta.tags)))


def get_tag_name(tag_id):
    db = request.db
    db.query(GET_TAG_BY_ID, tag_id)
    return db.results[0]


def get_tag_cloud():
    db = request.db
    db.query(GET_TAG_CLOUD)
    return db.results


def with_content(func):
    @wraps(func)
    def wrapper(content_id, **kwargs):
        try:
            content = get_single(content_id)
        except IndexError:
            abort(404)
        if not content:
            abort(404)
        return func(meta=Meta(content), **kwargs)
    return wrapper
