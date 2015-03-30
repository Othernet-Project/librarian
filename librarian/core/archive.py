"""
archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
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

from ..lib.squery import sqlin

from .metadata import add_missing_keys, clean_keys, Meta
from .downloads import get_spool_zip_path, get_zip_path, get_metadata


FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}

CONTENT_ORDER = ['-date(updated)', '-views']
INSERT_KEYS = (
    'md5',
    'url',
    'title',
    'images',
    'timestamp',
    'updated',
    'keep_formatting',
    'is_partner',
    'is_sponsored',
    'archive',
    'partner',
    'license',
    'language',
    'size',
)


def multiarg(query, n):
    """ Returns version of query where '??' is replaced by n placeholders """
    return query.replace('??', ', '.join('?' * n))


def with_tag(q):
    q.sets.natural_join('taggings')
    q.where += 'tag_id = :tag_id'


def get_count(tag=None):
    db = request.db
    q = db.Select('COUNT(*) as count', sets='zipballs')
    if tag:
        q.where += 'tag_id == :tag'
        q.sets.natural_join('taggings')
    db.query(q, tag=tag)
    return db.result.count


def get_search_count(terms, tag=None):
    terms = '%' + terms.lower() + '%'
    db = request.db
    q = db.Select('COUNT(*) as count', sets='zipballs',
                  where='title LIKE :terms')
    if tag:
        with_tag(q)
    db.query(q, terms=terms, tag_id=tag)
    return db.result.count


def get_content(offset=0, limit=0, tag=None):
    db = request.db
    q = db.Select(sets='zipballs', order=['-datetime(updated)', '-views'],
                  limit=limit, offset=offset)
    if tag:
        with_tag(q)
    db.query(q, tag_id=tag)
    return db.results


def get_single(md5):
    db = request.db
    q = db.Select(sets='zipballs', where='md5 = ?')
    db.query(q, md5)
    return db.result


def get_titles(ids):
    db = request.db
    q = db.Select(['title', 'md5'], sets='zipballs', where=sqlin('md5', ids))
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
    q = db.Select(sets='zipballs', where='title LIKE :terms',
                  order=CONTENT_ORDER, limit=limit, offset=offset)
    if tag:
        with_tag(q)
    db.query(q, terms=terms, tag_id=tag)
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
    clean_keys(meta)
    meta['md5'] = md5
    meta['updated'] = datetime.now()
    meta['size'] = os.stat(path).st_size
    return meta


def add_meta_to_db(db, metadata, replaced):
    with db.transaction() as cur:
        logging.debug("Adding new content to archive database")
        q = db.Replace('zipballs', cols=INSERT_KEYS)
        db.executemany(q, metadata)
        rowcount = cur.rowcount
        logging.debug("Removing replaced content from archive database")
        if replaced:
            q = db.Delete('zipballs', where=sqlin('md5', replaced))
            print(q)
        db.executemany(q, replaced)
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
    db = request.db
    failed = []
    for md5, path in ((h, get_zip_path(h)) for h in hashes):
        logging.debug("<%s> removing from archive (#%s)" % (path, md5))
        if path is None:
            failed.append(md5)
            continue
        try:
            os.unlink(path)
        except OSError as err:
            logging.error("<%s> cannot delete: %s" % (path, err))
            failed.append(md5)
            continue
    with db.transaction() as cur:
        in_md5s = sqlin('md5', hashes)
        logging.debug("Removing %s items from archive database" % len(hashes))
        q = db.Delete('zipballs', where=in_md5s)
        db.query(q, *hashes)
        rowcount = cur.rowcount
        q = db.Delete('taggings', where=in_md5s)
        db.query(q, *hashes)
    logging.debug("%s items removed from database" % rowcount)
    return failed


def zipball_count():
    """ Return the count of zipballs in archive

    :returns:   integer count
    """
    db = request.db
    q = db.Select('COUNT(*) as count', 'zipballs')
    db.query(q)
    return db.result.count


def last_update():
    """ Get timestamp of the last updated zipball

    :returns:   datetime object of the last updated zipball
    """
    db = request.db
    q = db.Select('updated', sets='zipballs', order='-updated', limit=1)
    db.query(q)
    res = db.result
    return res and res.updated


def add_view(md5):
    """ Increments the viewcount for zipball with specified MD5

    :param md5:     MD5 of the zipball
    :returns:       ``True`` if successful, ``False`` otherwise
    """
    db = request.db
    q = db.Update('zipballs', views='views + 1', where='md5 = ?')
    db.query(q, md5)
    assert db.cursor.rowcount == 1, 'Updated more than one row'
    return db.cursor.rowcount


def add_tags(meta, tags):
    """ Take content data and comma-separated tags and add the taggings """
    if not tags:
        return
    db = request.db

    # First ensure all tags exist
    with db.transaction():
        q = db.Insert('tags', cols=('name',))
        db.executemany(q, ({'name': t} for t in tags))

    # Get the IDs of the tags
    db.query(db.Select(sets='tags', where=sqlin('name', tags)), *tags)
    tags = db.results
    ids = (i['tag_id'] for i in tags)

    # Create taggings
    pairs = ({'md5': meta.md5, 'tag_id': i} for i in ids)
    tags_dict = {t['name']: t['tag_id'] for t in tags}
    meta.tags.update(tags_dict)
    with db.transaction():
        q = db.Insert('taggings', cols=('tag_id', 'md5'))
        db.executemany(q, pairs)
        q = db.Update('zipballs', tags=':tags', where='md5 = :md5')
        db.query(q, md5=meta.md5, tags=json.dumps(meta.tags))
    return tags


def remove_tags(meta, tags):
    """ Take content data nad comma-separated tags and removed the taggings """
    if not tags:
        return
    tag_ids = [meta.tags[name] for name in tags]
    meta.tags = dict((n, i) for n, i in meta.tags.items() if n not in tags)
    db = request.db
    with db.transaction():
        q = db.Delete('taggings',
                      where=['md5 = ?', sqlin('tag_id', tag_ids)])
        db.query(q, meta.md5, *tag_ids)
        q = db.Update('zipballs', tags=':tags', where='md5 = :md5')
        db.query(q, md5=meta.md5, tags=json.dumps(meta.tags))


def get_tag_name(tag_id):
    db = request.db
    q = db.Select('name', sets='tags', where='tag_id = ?')
    db.query(q, tag_id)
    return db.result


def get_tag_cloud():
    db = request.db
    q = db.Select(['name', 'tag_id', 'COUNT(taggings.tag_id) as count'],
                  sets=db.From('tags', 'taggings', join='NATURAL'),
                  group='taggings.tag_id',
                  order=['-count', 'name'])
    db.query(q)
    return db.results


def with_content(func):
    @wraps(func)
    def wrapper(content_id, **kwargs):
        conf = request.app.config
        try:
            content = get_single(content_id)
        except IndexError:
            abort(404)
        if not content:
            abort(404)
        zip_path = get_zip_path(content_id)
        assert zip_path is not None, 'Expected zipball to exist'
        meta = Meta(content, conf['content.covers'], zip_path)
        return func(meta=meta, **kwargs)
    return wrapper
