"""
options.py: User options management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import copy
import datetime
import json

from bottle import request, redirect

from bottle_utils.i18n import i18n_path


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return super(DateTimeEncoder, self).default(obj)


class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        super(DateTimeDecoder, self).__init__(object_hook=self.object_hook,
                                              *args,
                                              **kargs)

    def object_hook(self, obj):
        if '__type__' not in obj:
            return obj

        obj_type = obj.pop('__type__')
        try:
            return datetime(**obj)
        except Exception:
            obj['__type__'] = obj_type
            return obj


class Options(object):
    """A dict-like object with a callback that is invoked when changes are made
    to the object's state."""
    def __init__(self, data, onchange):
        self.onchange = onchange
        if isinstance(data, dict):
            self.__data = data
        else:
            self.__data = json.loads(data or '{}', cls=DateTimeDecoder)

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def items(self):
        return self.__data.items()

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value
        self.onchange()

    def __contains__(self, key):
        return key in self.__data

    def __delitem__(self, key):
        del self.__data[key]
        self.onchange()

    def __len__(self):
        return len(self.__data)

    def to_json(self):
        return json.dumps(self.__data, cls=DateTimeEncoder)

    def to_native(self):
        return copy.copy(self.__data)

    def apply(self):
        language = request.user.options.get('language')
        i18n_prefix = '/{0}/'.format(request.locale)
        # redirect only requests without a locale prefixed path
        if language and not request.original_path.startswith(i18n_prefix):
            redirect(i18n_path(locale=language))

        request.user.options['language'] = request.locale
