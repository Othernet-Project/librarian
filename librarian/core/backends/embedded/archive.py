"""
archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools
import json
import logging

from ...archive import BaseArchive, metadata


CONTENT_ORDER = ['-date(updated)', '-views']


def multiarg(query, n):
    """ Returns version of query where '??' is replaced by n placeholders """
    return query.replace('??', ', '.join('?' * n))


def with_tag(q):
    q.sets.natural_join('taggings')
    q.where += 'tag_id = :tag_id'


class AttrDict(dict):

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def row_to_dict(row):
    return AttrDict((key, row[key]) for key in row.keys())


def to_dict(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        row = func(*args, **kwargs)
        if not row:
            return row
        return row_to_dict(row)
    return wrapper


def to_dict_list(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        rows = func(*args, **kwargs)
        if not rows:
            return rows
        return map(row_to_dict, rows)
    return wrapper


class Transformation(object):
    pass


class Merge(Transformation):
    """Merge into parent"""
    pass


class Ignore(Transformation):
    """Ignores / deletes key and value"""
    pass


class Rename(Transformation):
    """Renames key to specified name"""
    def __init__(self, name):
        self.name = name


class EmbeddedArchive(BaseArchive):
    transformations = [
        {'content': Merge},
        {'replaces': Ignore},
        {'video': [
            {'size': Rename('resolution')}
        ]},
        {'image': [
            {'size': Rename('resolution')}
        ]}
    ]
    content_schema = {
        'generic': {},
        'html': {},
        'video': {},
        'audio': {'many': ['playlist']},
        'app': {},
        'image': {'many': ['album']},
        'playlist': {},
        'album': {}
    }

    def __init__(self, db, **config):
        self.db = db
        self.sqlin = lambda *args, **kw: self.db.sqlin.__func__(*args, **kw)
        super(EmbeddedArchive, self).__init__(**config)

    @to_dict
    def one(self):
        return self.db.result

    @to_dict_list
    def many(self):
        return self.db.results

    def _serialize(self, metadata, transformations):
        for transformer in transformations:
            ((key, action),) = transformer.items()
            if isinstance(action, list) and key in metadata:
                self._serialize(metadata[key], action)
            elif action is Merge:
                value = metadata.pop(key, None)
                if value is not None:
                    metadata.update(value)
            elif action is Ignore:
                metadata.pop(key, None)
            elif isinstance(action, Rename):
                value = metadata.pop(key, None)
                if value is not None:
                    metadata[action.name] = value

    def _query(self, q, terms, tag, lang, content_type):
        if tag:
            with_tag(q)

        if lang:
            q.where += 'language = :lang'

        if terms:
            terms = '%' + terms.lower() + '%'
            q.where += ('title LIKE :terms OR '
                        'publisher LIKE :terms OR '
                        'keywords LIKE :terms')

        if content_type:
            # get integer representation of content type
            content_type_id = metadata.CONTENT_TYPES[content_type]
            q.where += '("content_type" & :content_type) == :content_type'
        else:
            # exclude content types that cannot be displayed on the mixed type
            # content list
            content_type_id = sum([metadata.CONTENT_TYPES[name]
                                   for name in self.exclude_from_content_list])
            q.where += '("content_type" & :content_type) != :content_type'

        self.db.query(q,
                      terms=terms,
                      tag_id=tag,
                      lang=lang,
                      content_type=content_type_id)

    def get_count(self, terms=None, tag=None, lang=None, content_type=None):
        q = self.db.Select('COUNT(*) as count',
                           sets='zipballs',
                           where='disabled = 0')
        self._query(q, terms, tag, lang, content_type)
        return len(self.many)

    def get_content(self, terms=None, offset=0, limit=0, tag=None, lang=None,
                    content_type=None):
        # TODO: tests
        q = self.db.Select(sets='zipballs',
                           where='disabled = 0',
                           order=CONTENT_ORDER,
                           limit=limit,
                           offset=offset)
        self._query(q, terms, tag, lang, content_type)
        results = self.many()
        if results and content_type in self.prefetchable_types:
            for meta in results:
                self._fetch(content_type, meta['md5'], meta)

        return results

    def _fetch(self, table, content_id, dest, many=False):
        q = self.db.Select(sets=table, where='md5 = ?')
        self.db.query(q, content_id)
        dest[table] = self.one() if not many else self.many()
        for relation, related_tables in self.content_schema[table].items():
            for rel_table in related_tables:
                self._fetch(rel_table,
                            content_id,
                            dest[table],
                            many=relation == 'many')

    def get_single(self, content_id):
        q = self.db.Select(sets='zipballs', where='md5 = ?')
        self.db.query(q, content_id)
        data = self.one()
        if data:
            for content_type, mask in metadata.CONTENT_TYPES.items():
                if data['content_type'] & mask == mask:
                    self._fetch(content_type, content_id, data)
        return data

    def get_multiple(self, content_ids, fields=None):
        q = self.db.Select(what=['*'] if fields is None else fields,
                           sets='zipballs',
                           where=self.sqlin('md5', content_ids))
        self.db.query(q, *content_ids)
        return self.many()

    def content_for_domain(self, domain):
        # TODO: tests
        q = self.db.Select(sets='zipballs',
                           where='url LIKE :domain AND disabled = 0',
                           order=CONTENT_ORDER)
        domain = '%' + domain.lower() + '%'
        self.db.query(q, domain=domain)
        return self.many()

    def _write(self, table_name, data, shared_data=None):
        data.update(shared_data)
        primitives = {}
        for key, value in data.items():
            if isinstance(value, dict):
                self._write(key, value, shared_data=shared_data)
            elif isinstance(value, list):
                for row in value:
                    self._write(key, row, shared_data=shared_data)
            else:
                primitives[key] = value

        q = self.db.Replace(table_name, cols=primitives.keys())
        self.db.query(q, **primitives)

    def add_meta_to_db(self, metadata):
        with self.db.transaction() as cur:
            logging.debug("Adding new content to archive database")
            replaces = metadata.get('replaces')
            self._serialize(metadata, self.transformations)
            self._write('zipballs',
                        metadata,
                        shared_data={'md5': metadata['md5']})
            if replaces:
                msg = "Removing replaced content from archive database."
                logging.debug(msg)
                q = self.db.Delete('zipballs', where='md5 = ?')
                self.db.query(q, replaces)

        return True

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
        res = self.one()
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
        tags = self.many()
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
        return self.one()

    def get_tag_cloud(self):
        q = self.db.Select(
            ['name', 'tag_id', 'COUNT(taggings.tag_id) as count'],
            sets=self.db.From('tags', 'taggings', join='NATURAL'),
            group='taggings.tag_id',
            order=['-count', 'name']
        )
        self.db.query(q)
        return self.many()

    def needs_formatting(self, md5):
        """ Whether content needs formatting patch """
        q = self.db.Select('keep_formatting', sets='zipballs', where='md5 = ?')
        self.db.query(q, md5)
        return not self.one()['keep_formatting']

    def get_content_languages(self):
        q = 'SELECT DISTINCT language FROM zipballs'
        self.db.query(q)
        return [row['language'] for row in self.many()]
