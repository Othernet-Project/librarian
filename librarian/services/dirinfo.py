from __future__ import unicode_literals

import logging
import os
import re

from bottle_utils.common import to_unicode

from librarian_content.facets.base import CDFObject
from librarian_core.exts import ext_container as exts


class DirInfo(CDFObject):
    DATABASE_NAME = 'files'
    TABLE_NAME = 'dirinfo'
    CACHE_KEY_TEMPLATE = u'dirinfo_{0}'
    FILENAME = '.dirinfo'
    ENTRY_REGEX = re.compile(r'(\w+)\[(\w+)\]')
    NO_LANGUAGE = ''
    TEXT_KEYS = ('name', 'description', 'publisher', 'keywords', 'cover')
    FIELDS = (
        'name',
        'description',
        'icon',
        'cover',
        'publisher',
        'keywords',
        'view',
    )

    def get(self, language, key, default=None):
        try:
            return self._data[language][key]
        except KeyError:
            try:
                value = self._data[self.NO_LANGUAGE][key]
            except KeyError:
                return default
            else:
                return default if value is None else value

    def set(self, key, value, language=NO_LANGUAGE):
        self._data.setdefault(language, {})
        self._data[language][key] = value

    def clean_data(self):
        cleaned = {}
        for lang in self._data:
            cleaned[lang] = {}
            for k, v in self._data[lang].items():
                if k not in self.FIELDS:
                    continue  # ignore keys we cannot store
                cleaned[lang][k] = v
        return cleaned

    def store(self):
        """Store dirinfo data structure in database."""
        db = self.supervisor.exts.databases[self.DATABASE_NAME]
        data = self.clean_data() or {self.NO_LANGUAGE: {}}
        for language, info in data.items():
            to_write = dict(path=self.path, language=language)
            to_write.update(info)
            query = db.Replace(self.TABLE_NAME,
                               constraints=['path', 'language'],
                               cols=to_write.keys())
            db.execute(query, to_write)

    def delete(self):
        db = self.supervisor.exts.databases[self.DATABASE_NAME]
        query = db.Delete(self.TABLE_NAME, where='path = %s')
        db.execute(query, (self.path,))
        self.supervisor.exts.cache.delete(self.get_cache_key(self.path))

    def read_file(self):
        """Read dirinfo file from disk."""
        info_file_path = os.path.join(self.path, self.FILENAME)
        fsal = self.supervisor.exts.fsal
        if fsal.exists(info_file_path):
            try:
                with fsal.open(info_file_path, 'r') as info_file:
                    info = [to_unicode(line) for line in info_file.readlines()]

                for line in info:
                    key, value = line.split('=')
                    match = self.ENTRY_REGEX.match(key)
                    if match:
                        (key, language) = match.groups()
                    else:
                        language = self.NO_LANGUAGE

                    self._data.setdefault(language, {})
                    self._data[language][key] = value.strip()
            except Exception:
                self._data = dict()
                msg = ".dirinfo reading of {0} failed.".format(self.path)
                logging.exception(msg)

    @classmethod
    def search(cls, supervisor, terms=None, language=None):
        db = exts.databases[cls.DATABASE_NAME]
        q = db.Select(sets=cls.TABLE_NAME, what='path')
        if language:
            q.where += 'language=%(language)s'
        if terms:
            q.where += ' OR '.join(
                '{} ILIKE %(terms)s'.format(key) for key in cls.TEXT_KEYS)
            terms = '%' + terms.lower() + '%'
        rows = db.fetchiter(q, dict(language=language, terms=terms))
        paths = (r['path'] for r in rows)
        return cls.from_db(supervisor, paths).itervalues()

    @classmethod
    def fetch(cls, db, paths):
        query = db.Select(sets=cls.TABLE_NAME, where=db.sqlin('path', paths))
        for row in db.fetchiter(query, paths):
            if row:
                raw_data = cls.row_to_dict(row)
                language = raw_data.pop('language', None) or cls.NO_LANGUAGE
                yield (raw_data.pop('path'), {language: raw_data})
