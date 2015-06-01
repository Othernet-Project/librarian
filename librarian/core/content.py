"""
content.py: Low-level content asset management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re
import json

import scandir


COMP_RE = re.compile(r'([0-9a-f]{2,3})')  # path component
MD5_RE = re.compile(r'[0-9a-f]{32}')  # complete md5 hexdigest
HEX_PATH = r'(/[0-9a-f]{3}){10}/[0-9a-f]{2}$'  # md5-based dir path


def fnwalk(path, fn, shallow=False):
    """
    Walk directory tree top-down until directories of desired length are found

    This generator function takes a ``path`` from which to begin the traversal,
    and a ``fn`` object that selects the paths to be returned. It calls
    ``os.listdir()`` recursively until either a full path is flagged by ``fn``
    function as valid (by returning a truthy value) or ``os.listdir()`` fails
    with ``OSError``.

    This function has been added specifically to deal with large and deep
    directory trees, and it's therefore not advisable to convert the return
    values to lists and similar memory-intensive objects.

    The ``shallow`` flag is used to terminate further recursion on match. If
    ``shallow`` is ``False``, recursion continues even after a path is matched.

    For example, given a path ``/foo/bar/bar``, and a matcher that matches
    ``bar``, with ``shallow`` flag set to ``True``, only ``/foo/bar`` is
    matched. Otherwise, both ``/foo/bar`` and ``/foo/bar/bar`` are matched.
    """
    if fn(path):
        yield path
        if shallow:
            return

    try:
        entries = scandir.scandir(path)
    except OSError:
        return

    for entry in entries:
        if entry.is_dir():
            for child in fnwalk(entry.path, fn, shallow):
                yield child


def filewalk(root):
    """Discover and yield all files found in the specified `root` folder."""
    for entry in scandir.scandir(root):
        if entry.is_dir():
            for child in filewalk(entry.path):
                yield child
        else:
            yield entry.path


def content_path_components(s):
    """ Extracts path components from and s or a path

    The ``s`` argument should be content ID (md5 hexdigest) or content path.

    This function returns a list of 11 components where first 10 contain 3 hex
    digits each, and last one contains only 2 digits.
    """
    if os.sep in s:
        s = s.replace(os.sep, '')
    if not MD5_RE.match(s):
        return []
    return COMP_RE.findall(s)


def to_path(md5, prefix=None):
    """ Convert content ID (md5 hexdigest) to path

    Optional prefix can be specified which is prepended to the converted path.
    The prefix is always normalized to platform's path style. If `md5` is not
    a valid value, `None` will be returned.
    """
    path = os.sep.join(content_path_components(md5))
    if not path:
        return None

    if prefix:
        prefix = prefix.replace('\\', '/')
        return os.path.join(os.path.normpath(prefix), path)
    return path


def to_md5(path):
    """ Convert path to content ID """
    return ''.join(content_path_components(path))


def find_content_dirs(basedir):
    """ Find all content directories within basedir

    This function matches all MD5-based directory structures within the
    specified base directory. It uses glob patterns to do this.

    The returned value is an iterator. It's highly recommended to use it as is
    (e.g., without converting it to a list) due to increased memory usage with
    large number of directories.
    """
    rxp = re.compile(basedir + HEX_PATH)
    for path in fnwalk(basedir, lambda p: rxp.match(p)):
        yield path


def find_infos(basedir):
    """ Find all info.json files and decode them

    Retrns an iterator that yields three-tuples of info.json path, decoded
    info.json metadata, and md5 hexdigest matching the path.
    """
    for path in find_content_dirs(basedir):
        infopath = os.path.join(path, 'info.json')
        if not os.path.exists(infopath):
            continue
        with open(infopath, 'r') as f:
            data = json.load(f, 'utf8')
        relpath = os.path.relpath(path, basedir)
        yield (infopath, data, to_md5(relpath))


def get_meta(basedir, md5, meta_filename='info.json', encoding='utf8'):
    """ Find info.json at path matching specified md5 ID

    This function looks up the path matching the specified md5 and returns
    parsed metadata.

    This function does not trap the ``ValueError`` exception raised by json
    module if metadata cannot be parsed.

    If the metadata file is not found, ``IOError`` is raised.
    """
    path = to_path(md5, prefix=basedir)
    infopath = os.path.join(path, meta_filename)
    with open(infopath, 'rb') as f:
        data = json.load(f, encoding)
    return data


def get_content_size(basedir, md5):
    """ Return the size of the content folder matching the given md5 ID."""
    content_path = to_path(md5, prefix=basedir)
    return os.stat(content_path).st_size
