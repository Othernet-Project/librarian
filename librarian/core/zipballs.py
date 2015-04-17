"""
zipballs.py: functions for working with zipballs

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import zipfile

from . import content


def validate(path):
    """ Validates the zipball

    This function validates ``path`` and returns ``True`` if it points to a
    valid content zipball, otherwise returning ``False``.

    For a content zipball to be considered valid it must:

    - have .zip extension
    - have a md5 that matches an MD5 hash
    - be a valid zip file (according to its magic number)
    - all paths in the zipball are under directory of same name as file (and
      there are, by extension, no absolute paths)
    - contain a file called info.json inside the directory
    - contain a file called index.html inside the directory

    The checks are performed from least expensive to most expensive and the
    first check that fails immediately returns ``False``.
    """
    # Inspect extension
    if not path.endswith('.zip'):
        return False
    # Inspect filename
    md5, _ = os.path.splitext(os.path.basename(path))
    if not content.MD5_RE.match(md5):
        return False
    # Inspect zipfile magic number
    if not zipfile.is_zipfile(path):
        return False
    # Inspect contents
    zfile = zipfile.ZipFile(path)
    md5dir = '{}/'.format(md5)
    names = zfile.namelist()
    print(names)
    if not names:
        return False
    if not all([n.startswith(md5dir) for n in names]):
        return False
    if '{}info.json'.format(md5dir) not in names:
        return False
    if '{}index.html'.format(md5dir) not in names:
        return False
    return True
