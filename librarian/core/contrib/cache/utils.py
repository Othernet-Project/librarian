import hashlib

from bottle_utils.common import to_bytes


def generate_key(*args, **kwargs):
    """Helper function to generate the md5 hash of all the passed in args."""
    md5 = hashlib.md5()

    for data in args:
        md5.update(to_bytes(data))

    for key, value in kwargs.items():
        md5.update(to_bytes(key) + to_bytes(value))

    return md5.hexdigest()


def strip_protocol(url, sep='://'):
    return url[url.find(sep) + len(sep):] if sep in url else url
