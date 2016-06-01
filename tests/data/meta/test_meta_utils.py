import pytest

import librarian.data.meta.utils as mod


@pytest.mark.parametrize('path,expected', [
    ('', ['']),
    ('/', ['/']),
    ('/path', ['/', '/path']),
    ('/path/to/file', ['/', '/path', '/path/to', '/path/to/file']),
    ('path', ['', 'path']),
    ('path/to/file', ['', 'path', 'path/to', 'path/to/file']),
])
def test_ancestors_of(path, expected):
    assert list(mod.ancestors_of(path)) == expected
