"""
zipballs.py: functions for working with zipballs

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import shutil
import zipfile
import tempfile
try:
    from io import BytesIO as StringIO
except ImportError:
    from cStringIO import StringIO

from . import content
from . import metadata


class ValidationError(Exception):
    """ Raised when zipball fails validation """
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg
        super(ValidationError, self).__init__(msg)


def get_info(zfile, prefix):
    """ Get metadata from zipball

    The ``prefix`` is the directory in which the metadata file is located,
    without the trailing slash. It is expected that the user will pass a valid
    path and no checking is performed.

    Metadata is parsed and ``ValueError`` is raised when it cannot be parsed.

    If metadata file is missing, ``KeyError`` is raised.

    Returns a parsed dict.
    """
    prefix = prefix.rstrip('/')
    infopath = '{}/info.json'.format(prefix)
    with zfile.open(infopath) as info:
        return json.load(info, 'utf8')


def validate(path):
    """ Validates the zipball

    This function validates the content zipball found at ``path`` and returns
    the metadata dict from the zipball if it is valid. If the zipball is not
    valid, ``ValidationError`` exception is raised. This exeption will be
    passed a human-readable message about why the validation failed.

    For a content zipball to be considered valid it must:

    - have .zip extension
    - have a md5 that matches an MD5 hash
    - be a valid zip file (according to its magic number)
    - all paths in the zipball are under directory of same name as file (and
      there are, by extension, no absolute paths)
    - contain a file called info.json inside the directory
    - have valid metadata in info.json
    - location of index file in metadata must be present

    The checks are performed from least expensive to most expensive and the
    first check that fails immediately raises.
    """
    # Inspect extension
    if not path.endswith('.zip'):
        raise ValidationError(path, 'invalid extension')
    # Inspect filename
    md5, _ = os.path.splitext(os.path.basename(path))
    if not content.MD5_RE.match(md5):
        raise ValidationError(path, 'invalid filename')
    # Inspect zipfile magic number
    if not zipfile.is_zipfile(path):
        raise ValidationError(path, 'invalid magic number, not a ZIP file')
        return
    # Inspect contents
    zfile = zipfile.ZipFile(path)
    md5dir = '{}/'.format(md5)
    names = zfile.namelist()
    if not names:
        raise ValidationError(path, 'ZIP file is empty')
    if not all([n.startswith(md5dir) for n in names]):
        raise ValidationError(path, 'invalid content directory strcuture')
    # Inspect metadata
    try:
        info = get_info(zfile, md5)
    except (KeyError, ValueError):
        raise ValidationError(path, 'missing or malformed metadata file')
    for k in metadata.REQUIRED_KEYS:
        if k not in info:
            raise ValidationError(path, "missing required key '{}'".format(k))
    indexpath = '{}/{}'.format(md5, info.get('index', 'index.html'))
    if indexpath not in names:
        raise ValidationError(path, "missing index at '{}'".format(indexpath))
    return info


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
    target_path = content.to_path(name, prefix=target)

    # Extract the zip file to temporary directory
    zfile = zipfile.ZipFile(path)
    zfile.extractall(tempdir)

    # Back up existing target directory with .backup suffix
    backup_path = backup(target_path)

    # Move the extracted directory to target path
    shutil.move(extract_path, target_path)

    # Remove the backup
    if backup_path:
        shutil.rmtree(backup_path)

    return target_path


def create(md5, basedir):
    """ Create an in-memory zipfile of content directory, essentially restore
    the original zipball structure. """
    content_path = content.to_path(md5, prefix=basedir)
    out = StringIO()
    with zipfile.ZipFile(out, 'w') as zipball:
        for path in content.filewalk(content_path):
            rel_content_path = os.path.relpath(path, content_path)
            zipball.write(path, os.path.join(md5, rel_content_path))
    out.seek(0)
    return out


def get_zip_path(md5, directory):
    """ Return zip path in a directory

    :param md5:         MD5 hex of the zipball
    :param directory:   directory in which to look for files
    """
    root = os.path.normpath(directory)
    filepath = os.path.join(root, md5 + '.zip')
    if os.path.exists(filepath):
        return filepath
    return None
