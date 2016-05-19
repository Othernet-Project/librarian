import os
import types

import mock
import pytest

import librarian.data.facets.archive as mod


# UNIT TESTS


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'save')
@mock.patch.object(mod.Processor, 'for_path')
def test__analyze(for_path, save, exts, processors):
    processors[0].is_entry_point.return_value = False
    for_path.return_value = processors
    callback = mock.Mock()
    # trigger processor updates
    archive = mod.Archive()
    archive._analyze('/path/to/file', False, callback)
    # the dict passed to save should contain the data from all processors
    expected = {0: '/path/to/file', 1: '/path/to/file'}
    exts.events.publish.assert_called_once_with(mod.Archive.ENTRY_POINT_FOUND,
                                                path='/path/to/file',
                                                facet_type=2)
    callback.assert_called_once_with(expected)


@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_blocking(_analyze):
    archive = mod.Archive()
    expected = {'path': _analyze.return_value}
    assert archive.analyze('path') == expected
    _analyze.assert_called_once_with('path', False, None)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_nonblocking(_analyze, exts):
    archive = mod.Archive()
    callback = mock.Mock()
    assert archive.analyze('path', callback=callback) == {}
    assert not _analyze.called
    assert exts.tasks.schedule.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test__scan_list_dir_fail(analyze, exts):
    exts.fsal.list_dir.return_value = (False, [], [])
    archive = mod.Archive()
    assert list(archive._scan('path', False, None, None, 0, 0)) == []
    assert not analyze.called


@pytest.mark.parametrize('maxdepth,levels', [
    (0, 1),
    (1, 2),
])
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test__scan_maxdepth(analyze, exts, maxdepth, levels):
    exts.fsal.list_dir.return_value = (True, [mock.Mock(rel_path='dir1')], [])
    archive = mod.Archive()
    expected = [analyze.return_value] * levels
    assert list(archive._scan('path', False, None, maxdepth, 0, 0)) == expected
    assert exts.fsal.list_dir.call_count == levels


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test__scan_callback(analyze, exts):
    callback = mock.Mock()
    exts.fsal.list_dir.return_value = (True, [mock.Mock(rel_path='dir1')], [])
    archive = mod.Archive()
    assert list(archive._scan('path', False, callback, 1, 0, 1)) == []
    callback.assert_called_once_with(analyze.return_value)
    kwargs = dict(path='dir1',
                  partial=False,
                  callback=callback,
                  maxdepth=1,
                  depth=1,
                  delay=1)
    exts.tasks.schedule.assert_called_once_with(archive.scan,
                                                kwargs=kwargs,
                                                delay=1)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test__scan_generator(analyze, exts):
    exts.fsal.list_dir.return_value = (True, [mock.Mock(rel_path='dir1')], [])
    archive = mod.Archive()
    # due to the above set up mock, it will yield infinitely so test only
    # a couple cases
    generator = archive._scan('path', False, None, None, 0, 0)
    assert next(generator) == analyze.return_value
    assert next(generator) == analyze.return_value
    assert next(generator) == analyze.return_value
    assert analyze.call_count == 3


@pytest.mark.parametrize('callback,ret_type', [
    (None, types.GeneratorType),
    (lambda x: x, list),
])
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test_scan_return_value(analyze, exts, callback, ret_type):
    exts.fsal.list_dir.return_value = (True, [], [])
    archive = mod.Archive()
    ret = archive.scan(callback=callback)
    assert isinstance(ret, ret_type)


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


@mock.patch.object(mod.Archive, '_save_parent')
@mock.patch.object(mod.Archive, 'scan')
def test_parent_not_found(scan, _save_parent, databases):
    scan.return_value = [{'/1': {'facet_types': 2},
                          '/2': {'facet_types': 8},
                          '/3': {'facet_types': 2}}]
    _save_parent.return_value = {'main': None, 'facet_types': 11}
    archive = mod.Archive(db=databases.facets)
    expected = {'path': '/does/not/exist',
                'main': None,
                'facet_types': ['generic', 'html', 'audio']}
    assert archive.parent('/does/not/exist') == expected
    scan.assert_called_once_with('/does/not/exist', partial=True, maxdepth=0)
    _save_parent.assert_called_once_with('/does/not/exist', facet_types=11)


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
    calls = [mock.call(set(non_existent), callback=archive.save),
             mock.call(set(non_existent), partial=True)]
    analyze.assert_has_calls(calls)


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
