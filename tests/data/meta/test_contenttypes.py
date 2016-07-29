import pytest

import librarian.data.meta.contenttypes as mod


@pytest.mark.parametrize('names,bitmask', [
    ('generic', 1),
    (['generic', 'generic'], 1),
    (['generic', 'audio'], 9),
    (['generic', 'audio', 'image'], 25),
    ([], 0),
])
def test_to_bitmask(names, bitmask):
    assert mod.ContentTypes.to_bitmask(names) == bitmask


@pytest.mark.parametrize('bitmask,names', [
    (1, ['generic']),
    (9, ['generic', 'audio']),
    (0, []),
])
def test_from_bitmask(bitmask, names):
    assert mod.ContentTypes.from_bitmask(bitmask) == names


@pytest.mark.parametrize('name,expected', [
    ('generic', True),
    ('html', True),
    ('video', True),
    ('audio', True),
    ('image', True),
    ('invalid', False),
])
def test_is_valid(name, expected):
    assert mod.ContentTypes.is_valid(name) is expected


def test_names():
    expected = ['audio', 'directory', 'generic', 'html', 'image', 'video']
    assert sorted(mod.ContentTypes.names()) == expected


@pytest.mark.parametrize('for_type,expected', [
    ('image', {'height': int, 'title': unicode, 'width': int}),
    (None, {'album': unicode,
            'author': unicode,
            'copyright': unicode,
            'cover': unicode,
            'description': unicode,
            'duration': float,
            'genre': unicode,
            'height': int,
            'icon': unicode,
            'keywords': unicode,
            'language': unicode,
            'main': unicode,
            'name': unicode,
            'outernet-styling': unicode,
            'publisher': unicode,
            'title': unicode,
            'view': unicode,
            'width': int}),
])
def test_keys(for_type, expected):
    assert mod.ContentTypes.keys(for_type) == expected


@pytest.mark.parametrize('for_type,expected', [
    ('image', ['title']),
    (None, ['album', 'author', 'description', 'genre', 'keywords', 'name',
            'publisher', 'title']),
])
def test_search_keys(for_type, expected):
    assert sorted(mod.ContentTypes.search_keys(for_type)) == expected
