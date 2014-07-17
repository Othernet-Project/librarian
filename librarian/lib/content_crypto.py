"""
content_crypto.py: Deals with public keys and content signatures

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os.path

from gnupg import GPG

__all__ = ('CryptoError', 'KeyImportError', 'DecryptionError', 'import_key',
           'extract_content',)


class CryptoError(BaseException):
    """ Base exception for all crypto-related errors """
    def __init__(self, msg, path=None):
        self.message = msg
        self.path = path
        super().__init__(msg)


class KeyImportError(CryptoError):
    """ Key import exception """
    pass


class DecryptionError(CryptoError):
    """ Decryption failure exception """
    pass


def import_key(keypath, keyring):
    """ Imports all keys from specified directory

    This function is idempotent, so importing the same key multiple times will
    always succeed.

    :param keypath:     path to armored key file
    :param keyring:     directory of the keyring
    """
    gpg = GPG(gnupghome=keyring)
    try:
        with open(keypath, 'r') as keyfile:
            result = gpg.import_keys(keyfile.read())
    except OSError:
        raise KeyImportError("Could not open '%s'" % keypath, keypath)
    if result.count == 0:
        raise KeyImportError("Could not import '%s'" % keypath, keypath)


def extract_content(path, keyring, output_dir, output_ext):
    """ Use the keyring to decrypt a document """
    name = os.path.splitext(os.path.basename(path))[0]
    gpg = GPG(gnupghome=keyring)
    new_path = os.path.join(output_dir, '.'.join([name, output_ext]))
    try:
        with open(path, 'rb') as content:
            data = gpg.decrypt(content.read(), output=new_path)
    except OSError as err:
        raise DecryptionError("Could not open '%s'" % path, path)
    return new_path

