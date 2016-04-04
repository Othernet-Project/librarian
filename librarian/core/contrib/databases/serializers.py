import datetime
import json
import re

from .utils import to_datetime


NUMERIC_RE = re.compile(r'^[\d\.]+$')


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
        for key, value in obj.items():
            # keeps original value if not datetime
            obj[key] = to_datetime(value)

        return obj
