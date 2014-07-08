"""
test_crypto.py: Unit tests for ``librarian.content_crypto`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


from unittest import mock

import pytest

from librarian.content_crypto import *


def raise_os(*args, **kwargs):
    raise OSError()


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_keyring(open_p, GPG):
    """ Uses specified keyring """
    import_key(keypath='foo', keyring='bar')
    GPG.assert_called_once_with(gnupghome='bar')


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_import(open_p, GPG):
    """ Opens specified file and imports key """
    gpg = GPG.return_value
    fd = open_p.return_value.__enter__.return_value
    import_key(keypath='foo', keyring='bar')
    open_p.assert_called_once_with('foo', 'r')
    gpg.import_keys.assert_called_once_with(fd.read.return_value)


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_os_error(open_p, GPG):
    """ Should raise on failure to open given key file """
    open_p.side_effect = raise_os
    with pytest.raises(KeyImportError):
        import_key(keypath='foo', keyring='bar')


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_import_failure(open_p, GPG):
    """ Should raise on failure to import given key """
    gpg = GPG.return_value
    result = gpg.import_keys.return_value
    result.count = 0
    with pytest.raises(KeyImportError):
        import_key(keypath='foo', keyring='bar')


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_extract_uses_keyring(open_p, GPG):
    """ Should use provided keyring """
    gpg = GPG.return_value
    data = gpg.decrypt.return_value
    data.trust_level = 2
    data.TRUST_FULLY = 2
    extract_content('/foo/bar.sig', 'bar', '/baz', 'zip')
    GPG.assert_called_once_with(gnupghome='bar')


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_fails_if_bad_file(open_p, GPG):
    """ Should raise if file cannot be opened """
    open_p.side_effect = raise_os
    with pytest.raises(DecryptionError):
        extract_content('/foo/bar.sig', 'bar', '/baz', 'zip')


@mock.patch('librarian.content_crypto.GPG')
@mock.patch('builtins.open')
def test_extract_return_value(open_p, GPG):
    """ Should return new file path with provided extension """
    gpg = GPG.return_value
    data = gpg.decrypt.return_value
    data.trust_level = 2
    data.TRUST_FULLY = 2
    path = extract_content('/foo/bar.sig', 'bar', '/baz', 'zip')
    assert path == '/baz/bar.zip'

