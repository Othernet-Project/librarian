import datetime
import re

import dateutil.parser
import pytz


NUMERIC_RE = re.compile(r'^[\d\.]+$')


def is_string(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def utcnow():
    """Return a timezone aware datetime object in UTC."""
    return datetime.datetime.now(tz=pytz.utc)


def to_datetime(value):
    """Convert passed in value to datetime object or return original value in
    case it cannot be converted."""
    if value and is_string(value) and not NUMERIC_RE.match(value):
        try:
            return dateutil.parser.parse(value)
        except (ValueError, TypeError):
            pass

    return value


def from_csv(raw_value):
    return [val.strip() for val in (raw_value or '').split(',') if val]


def to_csv(values):
    return ','.join(values)


def row_to_dict(row):
    return dict((key, row[key]) for key in row.keys()) if row else {}
