import types

import mock
import pytest

import librarian.data.meta.archive as mod


# UNIT TESTS


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'MetaWrapper')
@mock.patch.object(mod.Archive.Processor, 'is_entry_point')
def test__analyze(is_entry_point, MetaWrapper, exts):
    is_entry_point.return_value = True
    expected = {'/path/to/file': MetaWrapper.return_value}
    # trigger processor updates
    archive = mod.Archive()
    assert archive._analyze('/path/to/file', True) == expected
    # the dict passed to save should contain the data from all processors
    exts.events.publish.assert_called_once_with(mod.Archive.ENTRY_POINT_FOUND,
                                                path='/path/to/file',
                                                content_type=1)
    data = {'content_types': 1,
            'path': '/path/to/file',
            'mime_type': None,
            'metadata': {u'': {}}}
    MetaWrapper.assert_called_once_with(data)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_blocking(_analyze, exts):
    archive = mod.Archive()
    _analyze.return_value = {'path': 'metadata'}
    assert archive.analyze('path') == _analyze.return_value
    _analyze.assert_called_once_with('path', False)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_nonblocking_call(_analyze, exts):
    archive = mod.Archive()
    callback = mock.Mock()
    assert archive.analyze(['path1', 'path2'], callback=callback) == {}
    assert not _analyze.called
    assert exts.tasks.schedule.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_analyze')
def test_analyze_nonblocking_result(_analyze, exts):
    _analyze.side_effect = lambda x, p: {x: 'meta'}
    exts.tasks.schedule.side_effect = lambda x: x()
    archive = mod.Archive()
    callback = mock.Mock()
    assert archive.analyze(['path1', 'path2'], callback=callback) == {}
    callback.assert_called_once_with({'path1': 'meta', 'path2': 'meta'})


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


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Processor, 'for_type')
def test__keep_supported(for_type, exts):
    # set up mocked processors that just write something in the dict
    proc = mock.Mock()
    proc.return_value.can_process.side_effect = lambda x: x.endswith('txt')
    for_type.return_value = proc
    # check if paths were filtered according to processability
    archive = mod.Archive()
    ret = archive._keep_supported(['f1.txt', 'f3.jpg', 'file4.txt'], 'text')
    assert ret == ['f1.txt', 'f3.jpg', 'file4.txt']


@pytest.mark.parametrize('src,expected,content_type', [
    ({'invalid': 2}, {}, 'generic',),
    ({'width': 1, 'test': 2, 'height': 3}, {'width': 1, 'height': 3}, 'image'),
])
@mock.patch.object(mod, 'exts')
def test__strip(exts, src, expected, content_type):
    archive = mod.Archive()
    assert archive._strip(src, content_type) == expected


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_refresh_parent')
@mock.patch.object(mod.Archive, 'get')
def test_parent_found(get, _refresh_parent, exts):
    get.return_value = {'path': 'meta'}
    archive = mod.Archive()
    assert archive.parent('path') == 'meta'
    get.assert_called_once_with('path', ignore_missing=True)
    assert not _refresh_parent.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_refresh_parent')
@mock.patch.object(mod.Archive, 'get')
def test_parent_not_found(get, _refresh_parent, exts):
    get.return_value = {}
    archive = mod.Archive()
    assert archive.parent('path') == _refresh_parent.return_value
    get.assert_called_once_with('path', ignore_missing=True)
    _refresh_parent.assert_called_once_with('path')


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_refresh_parent')
@mock.patch.object(mod.Archive, 'get')
def test_parent_force_refresh(get, _refresh_parent, exts):
    archive = mod.Archive()
    archive.parent('path', refresh='from source')
    assert not get.called
    _refresh_parent.assert_called_once_with('path', 'from source')


# INTEGRATION TESTS FOR DATABASE QUERIES


def merge_fs_with_meta(fs_data, metadata, content_type=None):
    for fs_entry in fs_data:
        # filter for specific content type, if specified
        if (content_type is not None and
                fs_entry['content_types'] & content_type != content_type):
            continue
        # merge all meta entries into their respective fs structure
        fs_entry = dict(fs_entry)
        for meta in metadata:
            if meta['fs_id'] == fs_entry['id']:
                lang = meta['language']
                fs_entry.setdefault(lang, {})
                fs_entry[lang][meta['key']] = unicode(meta['value'])
        yield fs_entry


def compare_result_sets(result, expected):
    assert len(expected) == len(result)
    for (path, data) in expected.items():
        item = result[path].unwrap()
        for (key, value) in data.items():
            assert item[key] == value


@mock.patch.object(mod, 'exts')
def test_for_parent(exts, populated_database):
    (fs_data, metadata, databases) = populated_database
    archive = mod.Archive(db=databases.meta)
    # test for path only
    iter_merged = merge_fs_with_meta(fs_data, metadata)
    expected = dict((item['path'], item) for item in iter_merged
                    if item['parent_id'] == fs_data[0]['id'])
    result = archive.for_parent(fs_data[0]['path'])
    # compare results against expected data
    compare_result_sets(result, expected)


@mock.patch.object(mod, 'exts')
def test_for_parent_content_type(exts, populated_database):
    (fs_data, metadata, databases) = populated_database
    archive = mod.Archive(db=databases.meta)
    # test for path with specific content type filtering involved
    content_types = mod.ContentTypes.from_bitmask(fs_data[0]['content_types'])
    for ctype in content_types:
        # filter expected data as the query should perform too
        bitmask = mod.ContentTypes.to_bitmask(ctype)
        iter_merged = merge_fs_with_meta(fs_data, metadata, bitmask)
        expected = dict((item['path'], item) for item in iter_merged
                        if item['parent_id'] == fs_data[0]['id'])
        result = archive.for_parent(fs_data[0]['path'], content_type=ctype)
        # compare results against expected filtered data
        compare_result_sets(result, expected)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'save_many')
@mock.patch.object(mod.Archive, 'analyze')
def test__attach_missing_none(analyze, save_many, exts):
    archive = mod.Archive()
    data = {'path': 'exists'}
    ret = archive._attach_missing(['path'], data, False)
    assert ret == data
    assert not analyze.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'analyze')
def test__attach_missing_partial(analyze, exts):
    archive = mod.Archive()
    # only one path will be requested in this test, so it's safe to return
    # only one entry
    analyze.side_effect = lambda paths, **kw: {list(paths)[0]: 'found'}
    data = {'path': 'exists'}
    ret = archive._attach_missing(['path', 'missing'], data, True)
    assert ret == {'path': 'exists', 'missing': 'found'}
    paths = set(['missing'])
    analyze.assert_has_calls([
        mock.call(paths, callback=archive.save_many),
        mock.call(paths, partial=True),
    ])


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'save_many')
@mock.patch.object(mod.Archive, 'analyze')
def test__attach_missing_impartial(analyze, save_many, exts):
    archive = mod.Archive()
    # only one path will be requested in this test, so it's safe to return
    # only one entry
    analyze.side_effect = lambda paths, **kw: {list(paths)[0]: 'found'}
    data = {'path': 'exists'}
    ret = archive._attach_missing(['path', 'missing'], data, False)
    assert ret == {'path': 'exists', 'missing': 'found'}
    analyze.assert_called_once_with(set(['missing']))
    save_many.assert_called_once_with({'missing': 'found'})


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_keep_supported')
def test_get_none_supported(_keep_supported, exts):
    db = exts.databases[mod.Archive.DATABASE_NAME]
    _keep_supported.return_value = []
    archive = mod.Archive()
    assert archive.get(['path1', 'path2'], content_type='some') == {}
    # make sure no db operations were executed at all
    assert not db.Select.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_attach_missing')
@mock.patch.object(mod.Archive, '_keep_supported')
def test_get_ignore_missing(_keep_supported, _attach_missing, exts):
    db = exts.databases[mod.Archive.DATABASE_NAME]
    db.fetchiter.return_value = ()
    paths = ['/path/invalid', '/another/invalid']
    archive = mod.Archive()
    assert archive.get(paths, ignore_missing=True) == {}
    assert not _attach_missing.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_attach_missing')
@mock.patch.object(mod.Archive, '_keep_supported')
def test_get_attach_missing(_keep_supported, _attach_missing, exts,
                            strip_wrappers):
    db = exts.databases[mod.Archive.DATABASE_NAME]
    db.fetchiter.return_value = ()
    paths = ['/path/invalid', '/another/invalid']
    archive = mod.Archive()
    # use unwrapped version because ``batched`` would turn the result
    # into a dict
    unwrapped = strip_wrappers(archive.get)
    ret = unwrapped(archive, paths, ignore_missing=False)
    _attach_missing.assert_called_once_with(paths, {}, True)
    assert ret == _attach_missing.return_value


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, '_keep_supported')
def test_get(_keep_supported, exts, populated_database):
    # keep supported just returns what it gets
    _keep_supported.side_effect = lambda x, y: x
    (fs_data, metadata, databases) = populated_database
    archive = mod.Archive(db=databases.meta)
    # pick the last existing content type from the entries in db
    found_types = mod.ContentTypes.from_bitmask(fs_data[-1]['content_types'])
    bitmask = mod.ContentTypes.to_bitmask(found_types[-1])
    # filter expected data as the query should perform too
    expected = dict((item['path'], item)
                    for item in merge_fs_with_meta(fs_data, metadata, bitmask))
    paths = expected.keys()
    result = archive.get(paths,
                         content_type=found_types[-1],
                         ignore_missing=True)
    # compare results against expected filtered data
    compare_result_sets(result, expected)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'get')
@mock.patch.object(mod.Archive, 'save')
@mock.patch.object(mod.Archive, 'scan')
def test__refresh_parent_no_source(scan, save, get, exts):
    path = '/path/parent'
    scan.return_value = [{'/path/parent/child': mock.Mock(content_types=4)}]
    get.return_value = {path: 'metadata'}
    archive = mod.Archive()
    assert archive._refresh_parent(path) == 'metadata'
    scan.assert_called_once_with(path, partial=True, maxdepth=0)
    save.assert_called_once_with({'path': path,
                                  'type': mod.DIRECTORY_TYPE,
                                  'mime_type': None,
                                  'content_types': 5})
    get.assert_called_once_with(path)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Archive, 'get')
@mock.patch.object(mod.Archive, 'save')
@mock.patch.object(mod.Archive, 'scan')
def test__refresh_parent_from_source(scan, save, get, exts):
    path = '/path/parent'
    source = {'/path/parent/child': mock.Mock(content_types=4)}
    get.return_value = {path: 'metadata'}
    archive = mod.Archive()
    assert archive._refresh_parent(path, source) == 'metadata'
    assert not scan.called
    save.assert_called_once_with({'path': path,
                                  'type': mod.DIRECTORY_TYPE,
                                  'mime_type': None,
                                  'content_types': 5})
    get.assert_called_once_with(path)


def pick_search_data(entries):
    titleless = (mod.ContentTypes.GENERIC, mod.ContentTypes.DIRECTORY)
    for entry in entries:
        found_types = mod.ContentTypes.from_bitmask(entry['content_types'])
        content_types = [ct for ct in found_types if ct not in titleless]
        if not content_types:
            # none of the found content types have a title key
            continue
        for (lang, meta) in entry.items():
            if isinstance(meta, dict) and 'title' in meta:
                return (content_types[0], lang, meta['title'].split()[0])


@mock.patch.object(mod, 'exts')
def test_search(exts, populated_database):
    (fs_data, metadata, databases) = populated_database
    archive = mod.Archive(db=databases.meta)
    # pick an existing content type
    entries = list(merge_fs_with_meta(fs_data, metadata))
    # find data suitable for search
    (content_type, lang, term) = pick_search_data(entries)
    bitmask = mod.ContentTypes.to_bitmask(content_type)
    # filter expected data as the query should perform too
    expected = dict((item['path'], item) for item in entries
                    if item['content_types'] & bitmask == bitmask and
                    term in item.get(lang, {}).get('title', ''))
    result = archive.search(term, content_type=content_type, language=lang)
    # compare results against expected filtered data
    assert len(result) == len(expected)
    assert sorted(result.keys()) == sorted(expected.keys())


@mock.patch.object(mod, 'exts')
def test_save(exts, databases):
    mocked_cache = mock.Mock()
    mocked_cache.get.return_value = None
    exts.cache = mocked_cache
    data = {
        'type': mod.FILE_TYPE,
        'path': '/path/to/file',
        'mime_type': 'image/jpeg',
        'content_types': mod.ContentTypes.to_bitmask(mod.ContentTypes.VIDEO),
        'metadata': {
            'en': {
                'title': 'test',
                'description': 'another',
            }
        }
    }
    archive = mod.Archive(db=databases.meta)
    wrapper = archive.save(data)
    saved = wrapper.unwrap()
    assert saved['path'] == data['path']
    assert saved['content_types'] == data['content_types'] | 1
    assert saved['type'] == data['type']
    assert saved['metadata'] == data['metadata']
    assert saved['mime_type'] == data['mime_type']


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Processor, 'for_path')
def test_remove(for_path, exts, populated_database, processors):
    for_path.return_value = processors
    (fs_data, metadata, databases) = populated_database
    archive = mod.Archive(db=databases.meta)
    paths = [fs_data[0]['path'], fs_data[-1]['path']]
    archive.remove(paths)
    q = databases.meta.Select(sets='fs',
                              where=databases.meta.sqlin('path', paths))
    assert databases.meta.fetchall(q, paths) == []
    # make sure cleanup function was called
    calls = [mock.call(paths[0], fsal=archive._fsal),
             mock.call().deprocess(),
             mock.call(paths[1], fsal=archive._fsal),
             mock.call().deprocess()]
    for proc in processors:
        proc.assert_has_calls(calls)
