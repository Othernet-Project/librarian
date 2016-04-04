"""
archive.py: Facets archive

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import logging
import functools
import itertools

from .facets import Facets, FACET_TYPES
from .processors import get_facet_processors


ROOT_PATH = '.'


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


def split_path(path):
    parent, name = os.path.split(path)
    parent = parent or ROOT_PATH
    return parent, name


def filter_keys(data, valid_keys):
    if not data:
        return data

    filtered_data = {}
    for key, value in data.items():
        if key in valid_keys:
            filtered_data[key] = value
    return filtered_data


class FacetsArchive(object):

    ALL_KEYS = [
        'path',
        'file',
        'author',
        'description',
        'title',
        'genre',
        'album',
        'width',
        'height',
        'duration',
        'keywords',
        'copyright',
        'language',
        'outernet_formatting'
        'facet_types'
    ]

    SEARCH_KEYS = {
        'generic': [],
        'audio': ['author', 'title', 'genre', 'album'],
        'video': ['author', 'title', 'description'],
        'image': ['title'],
        'html': ['author', 'title', 'description', 'keywords']
    }

    FACET_TYPES_KEYS = {
        'common': ['path', 'file', 'facet_types'],
        'generic': [],
        'audio': ['author', 'title', 'album', 'genre', 'duration'],
        'video': ['author', 'title', 'description', 'width',
                  'height', 'duration'],
        'image': ['title', 'width', 'height'],
        'html': ['author', 'title', 'description', 'keywords', 'language',
                 'copyright', 'outernet_formatting']
    }

    TABLE = 'facets'

    def __init__(self, fsal, db, config):
        self.fsal = fsal
        self.db = db
        self.config = config

    @to_dict
    def one(self, *args, **kwargs):
        return self.db.fetchone(*args, **kwargs)

    def many(self, *args, **kwargs):
        rows = self.db.fetchall(*args, **kwargs)
        return (AttrDict(zip(self.ALL_KEYS, r)) for r in rows)

    def get_facets(self, path, init=False, facet_type=None):
        parent, name = split_path(path)
        q = self.db.Select(sets=self.TABLE, where='path = %s and file =%s')
        data = self.one(q, (parent, name))
        if not data and init:
            data = {'path': parent, 'file': name, 'facet_types': 1}
        if facet_type:
            data = self.apply_key_filter(data, facet_type)
        if data:
            return Facets(supervisor=None, path=None, data=data)

    def get_all_facets(self, dirpath, facet_type=None):
        params = {'path': dirpath}
        q = self.db.Select(sets=self.TABLE, where='path = %(path)s')
        if facet_type:
            q.where += 'facet_types = %(type)s'
            params['type'] = facet_type
        data = self.many(q, params)
        return (Facets(supervisor=None, path=None, data=d) for d in data)

    def update_facets(self, path):
        processors = get_facet_processors(path)
        if not processors:
            return
        facets = self.get_facets(path, init=True)
        for processor in processors:
            processor.process_file(facets, path)
        return self.save_facets(facets)

    def remove_facets(self, path):
        facets = self.get_facets(path)
        if not facets:
            return
        processors = get_facet_processors(path)
        for processor in processors:
            processor.deprocess_file(facets, path)
        with self.db.transaction():
            parent, name = split_path(path)
            query = self.db.Delete(self.TABLE, where='path = %s and file = %s')
            self.db.execute(query, (parent, name))

    def save_facets(self, facets):
        facets = self.cleanse(facets)
        with self.db.transaction():
            q = self.db.Replace(self.TABLE,
                                constraints=['path', 'file'],
                                cols=facets.keys())
            self.db.execute(q, facets)
        return facets

    def search(self, terms=None, facet_type=None):
        q = self.db.Select(sets=self.TABLE)
        facet_type_id = self._generate_filter(q,
                                              terms=terms,
                                              facet_type=facet_type)
        terms = '%' + terms.lower() + '%'
        params = dict(terms=terms, facet_type=facet_type_id)
        results = self.db.fetchiter(q, params)
        return (Facets(None, None, data=row) for row in results)

    def _generate_filter(self, q, terms=None, facet_type=None):
        if terms:
            cols = self._search_keys(facet_type)
            q.where += ' OR '.join(
                '{} ILIKE %(terms)s'.format(col) for col in cols)
        if facet_type:
            q.where += '(facet_types & %(facet_type)s) = %(facet_type)s'
            return FACET_TYPES[facet_type]

    def _search_keys(self, facet_type=None):
        if facet_type:
            keys = self.SEARCH_KEYS[facet_type]
        else:
            keys = itertools.chain(*self.SEARCH_KEYS.itervalues())
        return set(keys)

    def clear_and_reload(self):
        with self.db.transaction():
            self.clear()
            self.reload()

    def clear(self):
        q = self.db.Delete(self.TABLE)
        self.db.execute(q)

    def reload(self, path=None):
        path = path or ROOT_PATH
        (success, dirs, files) = self.fsal.list_dir(path)
        if success:
            for f in files:
                logging.debug("Adding file to facets: '{}'".format(f.rel_path))
                self.update_facets(f.rel_path)
            for d in dirs:
                self.reload(d.rel_path)

    @classmethod
    def cleanse(cls, facets):
        return filter_keys(facets, cls.ALL_KEYS)

    @classmethod
    def apply_key_filter(cls, facets, facet_type):
        if facet_type not in cls.FACET_TYPES_KEYS:
            raise ValueError('Invalid facet_type to filter by: {}'.format(
                facet_type))

        master_keys = cls.FACET_TYPES_KEYS
        allowed_keys = master_keys['common'] + master_keys[facet_type]
        return filter_keys(facets, allowed_keys)

    @classmethod
    def create_partial(cls, path):
        parent, name = split_path(path)
        return dict(path=parent, file=name, facet_types=1)
