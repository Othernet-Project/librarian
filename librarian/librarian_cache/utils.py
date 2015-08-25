import hashlib


def is_string(obj):
    if 'basestring' not in globals():
        basestring = str
    return isinstance(obj, basestring)


def to_str(obj):
    try:
        return str(obj)
    except Exception:
        return obj.encode('ascii', 'ignore')


def generate_key(*args, **kwargs):
    """Helper function to generate the md5 hash of all the passed in args."""
    md5 = hashlib.md5()

    for data in args:
        md5.update(to_str(data))

    for key, value in kwargs.items():
        md5.update(to_str(key) + to_str(value))

    return md5.hexdigest()
