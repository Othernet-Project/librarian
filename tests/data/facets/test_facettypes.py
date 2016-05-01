import pytest

import librarian.data.facets.facettypes as mod


@pytest.mark.parametrize('names,bitmask', [
    ('generic', 1),
    (['generic', 'generic'], 1),
    (['generic', 'audio'], 9),
    (['generic', 'audio', 'image'], 25),
    ([], 0),
])
def test_to_bitmask(names, bitmask):
    assert mod.FacetTypes.to_bitmask(names) == bitmask


@pytest.mark.parametrize('bitmask,names', [
    (1, ['generic']),
    (9, ['generic', 'audio']),
    (0, []),
])
def test_from_bitmask(bitmask, names):
    assert mod.FacetTypes.from_bitmask(bitmask) == names


@pytest.mark.parametrize('name,expected', [
    ('generic', True),
    ('html', True),
    ('video', True),
    ('audio', True),
    ('image', True),
    ('invalid', False),
])
def test_is_valid(name, expected):
    assert mod.FacetTypes.is_valid(name) is expected


@pytest.mark.parametrize('include_meta,expected', [
    (False, ['audio', 'generic', 'html', 'image', 'video']),
    (True, ['audio', 'generic', 'html', 'image', 'updates', 'video']),
])
def test_names(include_meta, expected):
    assert sorted(mod.FacetTypes.names(include_meta=include_meta)) == expected


@pytest.mark.parametrize('for_type,specialized_only,expected', [
    ('image', True, ['height', 'title', 'width']),
    ('image', False, ['facet_types', 'height', 'path', 'title', 'width']),
    (None, True, ['album', 'author', 'copyright', 'description', 'duration',
                  'genre', 'height', 'keywords', 'language',
                  'outernet_formatting', 'title', 'width']),
    (None, False, ['album', 'author', 'copyright', 'description', 'duration',
                   'facet_types', 'genre', 'height', 'keywords', 'language',
                   'outernet_formatting', 'path', 'title', 'width']),
])
def test_keys(for_type, specialized_only, expected):
    assert sorted(mod.FacetTypes.keys(for_type, specialized_only)) == expected


@pytest.mark.parametrize('for_type,expected', [
    ('image', ['title']),
    ('generic', []),
    (None, ['album', 'author', 'description', 'genre', 'keywords', 'title']),
])
def test_search_keys(for_type, expected):
    assert sorted(mod.FacetTypes.search_keys(for_type)) == expected
