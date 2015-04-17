"""
zipballs.py: functions for working with zipballs

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import shutil
import zipfile
import tempfile

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


def backup(path):
    """ Moves the path to a path with .backup suffix """
    path = os.path.normpath(path.replace('\\', '/'))
    if not os.path.exists(path):
        return
    target = path + '.backup'
    os.rename(path, target)
    return target


def extract(path, target):
    """ Extract zipball at path to target path

    No validation of the zipball at path is performed. It is assumed that
    caller has performed necessary validation.

    Extraction process looks like this:
    - Zipfile is first extracted to a temporary directory specified by the
      operating system configuration.
    - The target path is calcualted based on zipfile name, and it is checked
      for already existing content.
    - Any existing content is renmaed with '.backup' suffix.
    - The extracted directory is then moved to target path.

    Function returns the path to which the zipball has been extracted.
    """
    # Calculate paths involved
    tempdir = tempfile.gettempdir()
    name, _ = os.path.splitext(os.path.basename(path))
    extract_path = os.path.join(tempdir, name)
    target_path = content.to_path(name)

    # Extract the zip file to temporary directory
    zfile = zipfile.ZipFile(path)
    zfile.extractall(tempdir)

    # Back up existing target directory with .backup suffix
    backup_path = backup(target_path)

    # Make sure target exists
    os.makedirs(os.path.dirname(target_path))

    # Move the extracted directory to target path
    shutil.move(extract_path, target_path)

    # Remove the backup
    if backup_path:
        shutil.rmtree(backup_path)

    return target_path
