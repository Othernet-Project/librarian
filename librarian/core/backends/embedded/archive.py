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
from datetime import datetime

from ...metadata import clean_keys, META_SPECIFICATION
from ...downloads import (get_spool_zip_path,
                          get_zip_path,
                          get_metadata,
                          get_md5_from_path)

from . import backend


db = backend.storage
config = backend.config

CONTENT_ORDER = ['-date(updated)', '-views']
INSERT_KEYS = META_SPECIFICATION.keys()


def multiarg(query, n):
    """ Returns version of query where '??' is replaced by n placeholders """
    return query.replace('??', ', '.join('?' * n))


def with_tag(q):
    q.sets.natural_join('taggings')
    q.where += 'tag_id = :tag_id'


def get_count(tag=None, lang=None, multipage=None):
    q = db.Select('COUNT(*) as count', sets='zipballs')
    if tag:
        q.where += 'tag_id == :tag'
        q.sets.natural_join('taggings')
    if lang:
        q.where += 'language = :lang'
    if multipage is not None:
        q.where += 'multipage = :multipage'
    db.query(q, tag=tag, lang=lang, multipage=multipage)
    return db.result.count


def get_search_count(terms, tag=None, lang=None, multipage=None):
    terms = '%' + terms.lower() + '%'
    q = db.Select('COUNT(*) as count', sets='zipballs',
                  where='title LIKE :terms')
    if tag:
        with_tag(q)
    if lang:
        q.where += 'language = :lang'
    if multipage is not None:
        q.where += 'multipage = :multipage'
    db.query(q, terms=terms, tag_id=tag, lang=lang, multipage=multipage)
    return db.result.count


def get_content(offset=0, limit=0, tag=None, lang=None, multipage=None):
    q = db.Select(sets='zipballs', order=['-datetime(updated)', '-views'],
                  limit=limit, offset=offset)
    if tag:
        with_tag(q)
    if lang:
        q.where += 'language = :lang'
    if multipage is not None:
        q.where += 'multipage = :multipage'
    db.query(q, tag_id=tag, lang=lang, multipage=multipage)
    return db.results


def get_single(md5):
    q = db.Select(sets='zipballs', where='md5 = ?')
    db.query(q, md5)
    return db.result


def get_titles(ids):
    q = db.Select(['title', 'md5'],
                  sets='zipballs',
                  where=db.sqlin('md5', ids))
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


def search_content(terms, offset=0, limit=0, tag=None, lang=None,
                   multipage=None):
    # TODO: tests
    terms = '%' + terms.lower() + '%'
    q = db.Select(sets='zipballs', where='title LIKE :terms',
                  order=CONTENT_ORDER, limit=limit, offset=offset)
    if tag:
        with_tag(q)
    if lang:
        q.where += 'language = :lang'
    if multipage is not None:
        q.where += 'multipage = :multipage'
    db.query(q, terms=terms, tag_id=tag, lang=lang, multipage=multipage)
    return db.results


def content_for_domain(domain):
    # TODO: tests
    q = db.Select(sets='zipballs',
                  where='url LIKE :domain',
                  order=CONTENT_ORDER)
    domain = '%' + domain.lower() + '%'
    db.query(q, domain=domain)
    return db.results


def prepare_metadata(md5, path):
    meta = get_metadata(path)
    clean_keys(meta)
    meta['md5'] = md5
    meta['updated'] = datetime.now()
    meta['size'] = os.stat(path).st_size
    return meta


def add_meta_to_db(metadata, replaced):
    with db.transaction() as cur:
        logging.debug("Adding new content to archive database")
        q = db.Replace('zipballs', cols=INSERT_KEYS)
        db.executemany(q, metadata)
        rowcount = cur.rowcount
        logging.debug("Removing replaced content from archive database")
        if replaced:
            q = db.Delete('zipballs', where=db.sqlin('md5', replaced))
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


def process_content(to_add, to_replace, to_delete, to_copy):
    content_dir = config['content.contentdir']
    rowcount = add_meta_to_db(to_add, to_replace)
    delete_obsolete(to_delete)
    copy_to_archive(to_copy, content_dir)
    return rowcount


def process(content, no_file_ops=False):
    to_add, to_replace, to_delete, to_copy = process_content_files(content)
    if no_file_ops:
        to_delete = []
        to_copy = []
    rows = process_content(to_add, to_replace, to_delete, to_copy)
    return rows, len(to_delete), len(to_copy)


def add_to_archive(hashes):
    content = ((h, get_spool_zip_path(h)) for h in hashes)
    rows, deleted, copied = process(content)
    logging.debug("%s items added to database", rows)
    logging.debug("%s items deleted from storage", deleted)
    logging.debug("%s items copied to storage", copied)
    return rows


def remove_from_archive(hashes):
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
        in_md5s = db.sqlin('md5', hashes)
        logging.debug("Removing %s items from archive database" % len(hashes))
        q = db.Delete('zipballs', where=in_md5s)
        db.query(q, *hashes)
        rowcount = cur.rowcount
        q = db.Delete('taggings', where=in_md5s)
        db.query(q, *hashes)
    logging.debug("%s items removed from database" % rowcount)
    return failed


def reload_data():
    zdir = config['content.contentdir']
    content = ((get_md5_from_path(f), os.path.join(zdir, f))
               for f in os.listdir(zdir)
               if f.endswith('.zip'))
    res = process(content, no_file_ops=True)
    return res[0]


def clear_and_reload():
    logging.debug('Content refill started.')
    q = db.Delete('zipballs')
    db.query(q)
    rows = reload_data()
    logging.info('Content refill finished for %s pieces of content', rows)


def zipball_count():
    """ Return the count of zipballs in archive

    :returns:   integer count
    """
    q = db.Select('COUNT(*) as count', 'zipballs')
    db.query(q)
    return db.result.count


def last_update():
    """ Get timestamp of the last updated zipball

    :returns:   datetime object of the last updated zipball
    """
    q = db.Select('updated', sets='zipballs', order='-updated', limit=1)
    db.query(q)
    res = db.result
    return res and res.updated


def add_view(md5):
    """ Increments the viewcount for zipball with specified MD5

    :param md5:     MD5 of the zipball
    :returns:       ``True`` if successful, ``False`` otherwise
    """
    q = db.Update('zipballs', views='views + 1', where='md5 = ?')
    db.query(q, md5)
    assert db.cursor.rowcount == 1, 'Updated more than one row'
    return db.cursor.rowcount


def add_tags(meta, tags):
    """ Take content data and comma-separated tags and add the taggings """
    if not tags:
        return

    # First ensure all tags exist
    with db.transaction():
        q = db.Insert('tags', cols=('name',))
        db.executemany(q, ({'name': t} for t in tags))

    # Get the IDs of the tags
    db.query(db.Select(sets='tags', where=db.sqlin('name', tags)), *tags)
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
    with db.transaction():
        q = db.Delete('taggings',
                      where=['md5 = ?', db.sqlin('tag_id', tag_ids)])
        db.query(q, meta.md5, *tag_ids)
        q = db.Update('zipballs', tags=':tags', where='md5 = :md5')
        db.query(q, md5=meta.md5, tags=json.dumps(meta.tags))


def get_tag_name(tag_id):
    q = db.Select('name', sets='tags', where='tag_id = ?')
    db.query(q, tag_id)
    return db.result


def get_tag_cloud():
    q = db.Select(['name', 'tag_id', 'COUNT(taggings.tag_id) as count'],
                  sets=db.From('tags', 'taggings', join='NATURAL'),
                  group='taggings.tag_id',
                  order=['-count', 'name'])
    db.query(q)
    return db.results


def needs_formatting(md5):
    """ Whether content needs formatting patch """
    q = db.Select('keep_formatting', sets='zipballs', where='md5 = ?')
    db.query(q, md5)
    return not db.result.keep_formatting
