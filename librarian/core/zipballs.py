"""
zipballs.py: Low-level functions for working with individual zipballs

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import shutil
import zipfile
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


def get_metadata(zfile, prefix, meta_filename='info.json', encoding='utf8'):
    """ Get metadata from zipball

    The ``prefix`` is the directory in which the metadata file is located,
    without the trailing slash. It is expected that the user will pass a valid
    path and no checking is performed.

    Metadata is parsed and ``ValueError`` is raised when it cannot be parsed.

    If metadata file is missing, ``KeyError`` is raised.

    Returns a parsed dict.
    """
    prefix = prefix.rstrip('/')
    infopath = '{0}/{1}'.format(prefix, meta_filename)
    with zfile.open(infopath) as info:
        raw_meta = json.load(info, encoding)
        return metadata.process_meta(raw_meta)


def validate(path, meta_filename='info.json'):
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

    The checks are performed from least expensive to most expensive and the
    first check that fails immediately raises.

    :param path:           Absolute path to zipball
    :param meta_filename:  Optional - name of file containing metadata
    :returns:              dict: validated and cleaned meta data
    """
    # Inspect path
    if not path or not os.path.exists(path):
        raise ValidationError(path, 'invalid path')
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
        meta = get_metadata(zfile, md5, meta_filename=meta_filename)
    except metadata.MetadataError as exc:
        raise ValidationError(path, str(exc))
    except (KeyError, ValueError):
        raise ValidationError(path, 'missing or malformed metadata file')
    else:
        return meta


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
    - Zipfile is first extracted to `target` path
    - If extraction fails, the partially extracted folder is deleted
    - The path of the target nested directory structure is calcualted based on
      zip filename
    - Any existing content is renamed with '.backup' suffix.
    - The extracted directory is then moved to target path.
    - If extraction is successful, the backup folder is deleted

    Function returns the path to which the zipball has been extracted.

    :param path:    absolute path to zipball
    :param target:  absolute path to directory where zipball is to be extracted
    """
    # Calculate paths involved
    name, _ = os.path.splitext(os.path.basename(path))
    target_path = content.to_path(name, prefix=target)
    extract_path = os.path.join(target, name)

    # Extract the zip file to target
    zfile = zipfile.ZipFile(path)
    try:
        zfile.extractall(target)
    except Exception:
        # if extraction fails, e.g. no space on device, remove partially
        # extracted folder if it exists at all, and re-raise
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        raise

    # Back up existing target directory with .backup suffix
    backup_path = backup(target_path)

    # Move the extracted directory to target path
    shutil.move(extract_path, target_path)

    # Remove the backup
    if backup_path and os.path.exists(backup_path):
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


def get_md5_from_path(path):
    """ Return MD5 hash from the filename

    This function will actually work with any path, not just ones that contain
    md5. It doesn't really check if the path contains valid md5 hexdigest.

    The function really returns the path without directory tree and extension
    portions.

    :param path:  path to signed file or zipball
    :returns:     md5 portion of the filename
    """
    return os.path.basename(os.path.splitext(path)[0])


def get_file(path, filename, no_read=False):
    """ Extract a single file from a zipball into memory

    :param path:      path to the zip file
    :param filename:  name of the file to extract
    :param no_read:   return file handle instead of file contents
    :returns:         file-object or contents of it, depending on `no_read`
    """
    try:
        # Note that we do NOT close the file handle if ``no_read`` is used.
        # This is intentional. If file handle is closed, the file handle we
        # return will be no good to the caller.
        raw_file = open(path, 'rb')
        zip_file = zipfile.ZipFile(raw_file)
        fd = zip_file.open(filename, 'r')
        if no_read:
            # We are retruning the file descriptor pointing to the zipfile
            # contents. This is not a real file descritor, just a file-like
            # object (it has read() but not seek()).
            return fd
        else:
            content = fd.read()
            fd.close()
            raw_file.close()  # We've read the content, so it's safe to close
            return content
    except zipfile.BadZipfile:
        raise ValidationError(path, "Invalid zipfile.")
    except Exception as exc:
        raise ValidationError(path, "Error while opening: {0}".format(exc))
