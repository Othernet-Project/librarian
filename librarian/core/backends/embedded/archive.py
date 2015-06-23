"""
archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json
import logging

from ...archive import BaseArchive


CONTENT_ORDER = ['-date(updated)', '-views']


def multiarg(query, n):
    """ Returns version of query where '??' is replaced by n placeholders """
    return query.replace('??', ', '.join('?' * n))


def with_tag(q):
    q.sets.natural_join('taggings')
    q.where += 'tag_id = :tag_id'


class EmbeddedArchive(BaseArchive):

    def __init__(self, db, **config):
        self.db = db
        self.sqlin = lambda *args, **kw: self.db.sqlin.__func__(*args, **kw)
        super(EmbeddedArchive, self).__init__(**config)

    def get_count(self, terms=None, tag=None, lang=None, multipage=None):
        q = self.db.Select('COUNT(*) as count',
                           sets='zipballs',
                           where='disabled = 0')
        if tag:
            with_tag(q)

        if lang:
            q.where += 'language = :lang'

        if multipage is not None:
            q.where += 'multipage = :multipage'

        if terms:
            terms = '%' + terms.lower() + '%'
            q.where += ('title LIKE :terms OR '
                        'publisher LIKE :terms OR '
                        'keywords LIKE :terms')

        self.db.query(q,
                      terms=terms,
                      tag_id=tag,
                      lang=lang,
                      multipage=multipage)

        return self.db.result.count

    def get_content(self, terms=None, offset=0, limit=0, tag=None, lang=None,
                    multipage=None):
        # TODO: tests
        q = self.db.Select(sets='zipballs',
                           where='disabled = 0',
                           order=CONTENT_ORDER,
                           limit=limit,
                           offset=offset)
        if tag:
            with_tag(q)

        if lang:
            q.where += 'language = :lang'

        if multipage is not None:
            q.where += 'multipage = :multipage'

        if terms:
            terms = '%' + terms.lower() + '%'
            q.where += ('title LIKE :terms OR '
                        'publisher LIKE :terms OR '
                        'keywords LIKE :terms')

        self.db.query(q,
                      terms=terms,
                      tag_id=tag,
                      lang=lang,
                      multipage=multipage)

        return self.db.results

    def get_single(self, content_id):
        q = self.db.Select(sets='zipballs', where='md5 = ?')
        self.db.query(q, content_id)
        return self.db.result

    def get_multiple(self, content_ids, fields=None):
        q = self.db.Select(what=['*'] if fields is None else fields,
                           sets='zipballs',
                           where=self.sqlin('md5', content_ids))
        self.db.query(q, *content_ids)
        return self.db.results

    def content_for_domain(self, domain):
        # TODO: tests
        q = self.db.Select(sets='zipballs',
                           where='url LIKE :domain AND disabled = 0',
                           order=CONTENT_ORDER)
        domain = '%' + domain.lower() + '%'
        self.db.query(q, domain=domain)
        return self.db.results

    def add_meta_to_db(self, metadata):
        with self.db.transaction() as cur:
            logging.debug("Adding new content to archive database")
            q = self.db.Replace('zipballs', cols=BaseArchive.db_fields)
            self.db.query(q, **metadata)
            rowcount = cur.rowcount
            replaces = metadata.get('replaces')
            if replaces:
                msg = "Removing replaced content from archive database."
                logging.debug(msg)
                q = self.db.Delete('zipballs', where='md5 = ?')
                self.db.query(q, replaces)

        return rowcount

    def remove_meta_from_db(self, content_id):
        with self.db.transaction() as cur:
            msg = "Removing {0} from archive database".format(content_id)
            logging.debug(msg)
            q = self.db.Delete('zipballs', where='md5 = ?')
            self.db.query(q, content_id)
            rowcount = cur.rowcount
            q = self.db.Delete('taggings', where='md5 = ?')
            self.db.query(q, content_id)
            return rowcount

    def clear_and_reload(self):
        logging.debug('Content refill started.')
        q = self.db.Delete('zipballs')
        self.db.query(q)
        rows = self.reload_content()
        logging.info('Content refill finished for %s pieces of content', rows)

    def last_update(self):
        """ Get timestamp of the last updated zipball

        :returns:   datetime object of the last updated zipball
        """
        q = self.db.Select('updated',
                           sets='zipballs',
                           order='-updated',
                           limit=1)
        self.db.query(q)
        res = self.db.result
        return res and res.updated

    def add_view(self, md5):
        """ Increments the viewcount for zipball with specified MD5

        :param md5:     MD5 of the zipball
        :returns:       ``True`` if successful, ``False`` otherwise
        """
        q = self.db.Update('zipballs', views='views + 1', where='md5 = ?')
        self.db.query(q, md5)
        assert self.db.cursor.rowcount == 1, 'Updated more than one row'
        return self.db.cursor.rowcount

    def add_tags(self, meta, tags):
        """ Take content data and comma-separated tags and add the taggings """
        if not tags:
            return

        # First ensure all tags exist
        with self.db.transaction():
            q = self.db.Insert('tags', cols=('name',))
            self.db.executemany(q, ({'name': t} for t in tags))

        # Get the IDs of the tags
        q = self.db.Select(sets='tags', where=self.sqlin('name', tags))
        self.db.query(q, *tags)
        tags = self.db.results
        ids = (i['tag_id'] for i in tags)

        # Create taggings
        pairs = ({'md5': meta.md5, 'tag_id': i} for i in ids)
        tags_dict = {t['name']: t['tag_id'] for t in tags}
        meta.tags.update(tags_dict)
        with self.db.transaction():
            q = self.db.Insert('taggings', cols=('tag_id', 'md5'))
            self.db.executemany(q, pairs)
            q = self.db.Update('zipballs', tags=':tags', where='md5 = :md5')
            self.db.query(q, md5=meta.md5, tags=json.dumps(meta.tags))

        return tags

    def remove_tags(self, meta, tags):
        """ Take content data nad comma-separated tags and removed the
        taggings """
        if not tags:
            return

        tag_ids = [meta.tags[name] for name in tags]
        meta.tags = dict((n, i) for n, i in meta.tags.items() if n not in tags)
        with self.db.transaction():
            q = self.db.Delete('taggings',
                               where=['md5 = ?',
                                      self.sqlin('tag_id', tag_ids)])
            self.db.query(q, meta.md5, *tag_ids)
            q = self.db.Update('zipballs', tags=':tags', where='md5 = :md5')
            self.db.query(q, md5=meta.md5, tags=json.dumps(meta.tags))

    def get_tag_name(self, tag_id):
        q = self.db.Select('name', sets='tags', where='tag_id = ?')
        self.db.query(q, tag_id)
        return self.db.result

    def get_tag_cloud(self):
        q = self.db.Select(
            ['name', 'tag_id', 'COUNT(taggings.tag_id) as count'],
            sets=self.db.From('tags', 'taggings', join='NATURAL'),
            group='taggings.tag_id',
            order=['-count', 'name']
        )
        self.db.query(q)
        return self.db.results

    def needs_formatting(self, md5):
        """ Whether content needs formatting patch """
        q = self.db.Select('keep_formatting', sets='zipballs', where='md5 = ?')
        self.db.query(q, md5)
        return not self.db.result.keep_formatting

    def get_content_languages(self):
        q = 'SELECT DISTINCT language FROM zipballs'
        self.db.query(q)
        return [row.language for row in self.db.results]
