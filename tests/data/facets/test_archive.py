import os

import mock
import pytest

import librarian.data.facets.archive as mod


# UNIT TESTS


@mock.patch.object(mod.Archive, '_save_parent')
@mock.patch.object(mod.Archive, 'save')
@mock.patch.object(mod.Processor, 'for_path')
def test__analyze(for_path, save, _save_parent, processors):
    processors[0].is_entry_point.return_value = False
    for_path.return_value = processors
    # trigger processor updates
    archive = mod.Archive()
    archive._analyze(['/path/to/file'])
    # the dict passed to save should contain the data from all processors
    expected = {0: '/path/to/file', 1: '/path/to/file'}
    save.assert_called_once_with(expected)
    _save_parent.assert_called_once_with('/path/to',
                                         main='file',
                                         facet_types=2)


@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_blocking(_analyze):
    archive = mod.Archive()
    archive.analyze('path', blocking=True)
    _analyze.assert_called_once_with(['path'])


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_nonblocking(_analyze, exts):
    archive = mod.Archive()
    archive.analyze('path', blocking=False)
    assert not _analyze.called
    exts.tasks.schedule.assert_called_once_with(archive._analyze,
                                                args=(['path'],))


@mock.patch.object(mod.Archive, 'partial')
@mock.patch.object(mod, 'exts')
def test_analyze_partial(exts, partial):
    archive = mod.Archive()
    expected = {'path1': partial.return_value, 'path2': partial.return_value}
    assert archive.analyze(['path1', 'path2'], partial=True) == expected
    partial.assert_has_calls([mock.call('path1'), mock.call('path2')])


@mock.patch.object(mod.Archive, 'partial')
@mock.patch.object(mod, 'exts')
def test_analyze_impartial(exts, partial):
    archive = mod.Archive()
    expected = {}
    assert archive.analyze(['path1', 'path2'], partial=False) == expected
    assert not partial.called


@mock.patch.object(mod.Processor, 'for_type')
def test__keep_supported(for_type):
    # set up mocked processors that just write something in the dict
    proc = mock.Mock()
    proc.return_value.can_process.side_effect = lambda x: x.endswith('txt')
    for_type.return_value = proc
    # check if paths were filtered according to processability
    archive = mod.Archive()
    ret = archive._keep_supported(['f1.txt', 'f3.jpg', 'file4.txt'], 'text')
    assert ret == ['f1.txt', 'f3.jpg', 'file4.txt']


@pytest.mark.parametrize('src,expected,facet_type', [
    (
        {'facet_types': 1, 'invalid': 2, 'path': 'test'},
        {'facet_types': 1, 'path': 'test'},
        'generic',
    ), (
        {'width': 1, 'test': 2, 'height': 3},
        {'width': 1, 'height': 3},
        'image',
    )
])
def test_strip(src, expected, facet_type):
    assert mod.Archive.strip(src, facet_type) == expected


@mock.patch.object(mod.Processor, 'for_type')
@mock.patch.object(mod.Processor, 'for_path')
def test_partial_for_path(for_path, for_type, processors):
    for_path.return_value = processors
    # trigger processor updates
    archive = mod.Archive()
    expected = {0: '/path/to/file', 1: '/path/to/file'}
    assert archive.partial('/path/to/file') == expected
    assert not for_type.called


@mock.patch.object(mod.Processor, 'for_type')
@mock.patch.object(mod.Processor, 'for_path')
def test_partial_for_type(for_path, for_type, processors):
    for_type.return_value = processors[0]
    # trigger processor updates
    archive = mod.Archive()
    expected = {0: '/path/to/file'}
    assert archive.partial('/path/to/file', facet_type='generic') == expected
    assert not for_path.called


# INTEGRATION TESTS FOR DATABASE QUERIES


@mock.patch.object(mod.Archive, 'scan')
def test_parent_found(scan, populated_database):
    (folders, facets, databases) = populated_database
    archive = mod.Archive(db=databases.facets)
    for folder in folders:
        bitmask = folder['facet_types']
        expected = dict(facet_types=mod.FacetTypes.from_bitmask(bitmask),
                        main=folder['main'],
                        path=folder['path'])
        assert archive.parent(folder['path']) == expected


@mock.patch.object(mod.Archive, 'scan')
def test_parent_not_found(scan, databases):
    archive = mod.Archive(db=databases.facets)
    expected = {'path': '/does/not/exist',
                'main': None,
                'facet_types': ['generic']}
    assert archive.parent('/does/not/exist') == expected
    scan.assert_called_once_with('/does/not/exist')


def compare_facet_sets(result, expected):
    assert len(expected) == len(result)
    for (path, data) in expected.items():
        item = result[path]
        for (k, v) in data.items():
            assert item[k] == v


def test_for_parent(populated_database):
    (folders, facets, databases) = populated_database
    archive = mod.Archive(db=databases.facets)
    # test for path only
    expected = dict((row['path'], row) for row in facets
                    if row['folder'] == folders[0]['id'])
    result = archive.for_parent(folders[0]['path'])
    # compare results against expected data
    compare_facet_sets(result, expected)
    # test for path with specific facet type filtering involved
    for facet_type in mod.FacetTypes.from_bitmask(folders[0]['facet_types']):
        # filter expected data as the query should perform too
        bitmask = mod.FacetTypes.to_bitmask(facet_type)
        expected = dict((row['path'], row) for row in facets
                        if row['folder'] == folders[0]['id'] and
                        row['facet_types'] & bitmask == bitmask)
        result = archive.for_parent(folders[0]['path'], facet_type=facet_type)
        # compare results against expected filtered data
        compare_facet_sets(result, expected)


@mock.patch.object(mod.Archive, '_keep_supported')
@mock.patch.object(mod.Archive, 'analyze')
def test_get(analyze, _keep_supported, populated_database):
    _keep_supported.side_effect = lambda x, y: x
    (folders, facets, databases) = populated_database
    archive = mod.Archive(db=databases.facets)
    # pick the last existing facet type from the entries in db
    existing_types = mod.FacetTypes.from_bitmask(facets[-1]['facet_types'])
    bitmask = mod.FacetTypes.to_bitmask(existing_types[-1])
    # filter expected data as the query should perform too
    expected = dict((row['path'], row) for row in facets
                    if row['facet_types'] & bitmask == bitmask)
    non_existent = ['/path/invalid', '/another/invalid']
    paths = expected.keys() + non_existent
    result = archive.get(paths, facet_type=existing_types[-1])
    # compare results against expected filtered data
    compare_facet_sets(result, expected)
    analyze.assert_called_once_with(set(non_existent), partial=True)


def first_facet_type(facets):
    # return the first encountered non-GENERIC facet type and bitmask
    for facet in facets:
        existing_types = mod.FacetTypes.from_bitmask(facet['facet_types'])
        for facet_type in existing_types:
            if facet_type != mod.FacetTypes.GENERIC:
                bitmask = mod.FacetTypes.to_bitmask(facet_type)
                return (facet_type, bitmask)


def test_search(populated_database):
    (folders, facets, databases) = populated_database
    archive = mod.Archive(db=databases.facets)
    # pick an existing facet type
    (facet_type, bitmask) = first_facet_type(facets)
    # pick first word in last entry's description
    term = facets[-1]['title'].split()[0]
    # filter expected data as the query should perform too
    expected = dict((row['path'], row) for row in facets
                    if row['facet_types'] & bitmask == bitmask and
                    term in row['title'])
    result = archive.search(term, facet_type=facet_type)
    # compare results against expected filtered data
    compare_facet_sets(result, expected)


@mock.patch.object(mod.Archive, '_save_parent')
def test_save(_save_parent, populated_database):
    (folders, facets, databases) = populated_database
    _save_parent.return_value = folders[0]
    data = {'path': '/path/to/file',
            'facet_types': mod.FacetTypes.to_bitmask(mod.FacetTypes.VIDEO)}
    archive = mod.Archive(db=databases.facets)
    saved = archive.save(data)
    parent = os.path.dirname(data['path'])
    _save_parent.assert_called_once_with(parent,
                                         facet_types=data['facet_types'])
    assert saved['path'] == data['path']
    assert saved['facet_types'] == data['facet_types']


@mock.patch.object(mod.Processor, 'for_path')
def test_remove(for_path, populated_database, processors):
    for_path.return_value = processors
    (folders, facets, databases) = populated_database
    archive = mod.Archive(db=databases.facets)
    paths = [facets[0]['path'], facets[-1]['path']]
    archive.remove(paths)
    q = databases.facets.Select(sets=mod.Archive.DATABASE_NAME,
                                where=databases.facets.sqlin('path', paths))
    assert databases.facets.fetchall(q, paths) == []
    # make sure cleanup function was called
    calls = map(mock.call, paths)
    for proc in processors:
        proc.return_value.deprocess_file.assert_has_calls(calls)
