import mock
import pytest

import librarian.data.meta.processors as mod

from librarian.data.meta.metadata import MetadataError


def test__merge():
    dest = {'en': {'title': 'Tests'},
            'rs': {'title': 'Testovi'}}
    source = {'en': {'description': 'Invention'},
              'rs': {'description': 'Izum'}}
    mod.Processor._merge(source, dest)
    assert dest == {'en': {'title': 'Tests', 'description': 'Invention'},
                    'rs': {'title': 'Testovi', 'description': 'Izum'}}


def test_get_path():
    proc = mod.GenericProcessor('/path/')
    assert proc.get_path() == '/path/'


def test_get_metadata_partial():
    class TestProc(mod.Processor):
        metadata_class = mock.Mock()
        name = 'generic'

    proc = TestProc('/path/file', partial=True)
    assert proc.get_metadata() == {}
    assert not proc.metadata_extractor.called


def test_get_metadata_no_metadata_class():
    proc = mod.GenericProcessor('/path/file', partial=False)
    assert proc.get_metadata() == {}


@mock.patch.object(mod.Processor, 'metadata_class')
def test_get_metadata_error(metadata_class):
    class TestProc(mod.Processor):
        metadata_class = mock.Mock()
        name = 'generic'

    proc = TestProc('/path/file', partial=False)
    proc.metadata_extractor.extract.side_effect = MetadataError()
    assert proc.get_metadata() == {}
    proc.metadata_extractor.extract.assert_called_once_with()


@mock.patch.object(mod.ImageProcessor, 'metadata_class')
def test_get_metadata(metadata_class):
    mocked_meta = dict(width=1, height=2, insignificant=3)
    metadata_class.return_value.extract.return_value = mocked_meta
    proc = mod.ImageProcessor('/path/file', partial=False)
    assert proc.get_metadata() == {'width': 1, 'height': 2}


@mock.patch.object(mod.Processor, 'get_metadata')
def test__add_metadata(get_metadata):
    get_metadata.return_value = {'width': 1, 'height': 2}
    dest = {'content_types': 1, 'metadata': {'': {'title': 'Fascinating'}}}
    proc = mod.GenericProcessor('/path/')
    proc._add_metadata(dest)
    expected = {'content_types': 1,
                'metadata': {'': {'title': 'Fascinating',
                                  'width': 1,
                                  'height': 2}}}
    assert dest == expected


@pytest.mark.parametrize('partial,expected', [
    (True, {'content_types': 5, 'metadata': 'kept', 'path': '/path/to'}),
    (False, {'content_types': 5,
             'metadata': 'kept',
             'path': '/path/to',
             'type': 0}),
])
@mock.patch.object(mod, 'exts')
def test__add_fs_data(exts, partial, expected):
    exts.fsal.isdir.return_value = False
    proc = mod.GenericProcessor('/path/to', partial=partial)
    dest = {'content_types': 4, 'metadata': 'kept'}
    proc._add_fs_data(dest)
    assert dest == expected


@mock.patch.object(mod.Processor, '_add_metadata')
@mock.patch.object(mod.Processor, '_add_fs_data')
def test_process(_add_fs_data, _add_metadata):
    _add_fs_data.side_effect = lambda x: x.update(test=3)
    path_meta = {'metadata': 'existing'}
    data = {'/path/to': path_meta}
    proc = mod.GenericProcessor('/path/to', data=data)
    proc.process()
    _add_fs_data.assert_called_once_with(path_meta)
    _add_metadata.assert_called_once_with(path_meta)
    assert proc.data == {'/path/to': {'metadata': 'existing', 'test': 3}}


@mock.patch.object(mod.Processor, 'get_path')
@mock.patch.object(mod.Processor, '_add_metadata')
@mock.patch.object(mod.Processor, '_add_fs_data')
def test_process_redirect(_add_fs_data, _add_metadata, get_path):
    get_path.return_value = '/another/'
    _add_fs_data.side_effect = lambda x: x.update(test=3)
    data = {'/path/to': {'metadata': 'existing'}}
    proc = mod.GenericProcessor('/path/to', data=data)
    proc.process()
    assert proc.data == {'/path/to': {'metadata': 'existing'},
                         '/another/': {'test': 3}}


@pytest.mark.parametrize('path,processable', [
    ('', False),
    ('/path/', False),
    ('/path/file', False),
    ('/path/file.ext', False),
    ('/path/file.tx', False),
    ('/path/file.txt', True),
])
def test_can_process(path, processable):
    class Proc(mod.Processor):
        EXTENSIONS = ['txt']

    assert Proc.can_process(path) is processable


def test_can_process_missing_extensions():
    class FailProc(mod.Processor):
        pass

    with pytest.raises(AttributeError):
        FailProc.can_process('test')


@mock.patch.object(mod.Processor, 'subclasses')
def test_for_path(subclasses):
    proc1 = mock.Mock()
    proc2 = mock.Mock()
    proc2.can_process.return_value = False
    proc3 = mock.Mock()
    subclasses.return_value = [proc1, proc2, proc3]
    assert list(mod.Processor.for_path('/path/file')) == [proc1, proc3]
    proc1.can_process.assert_called_once_with('/path/file')
    proc2.can_process.assert_called_once_with('/path/file')
    proc3.can_process.assert_called_once_with('/path/file')


def test_for_type_fail():
    with pytest.raises(RuntimeError):
        mod.Processor.for_type('invalid')


def test_for_type_success():
    class Proc(mod.Processor):
        name = 'awesome'

    assert mod.Processor.for_type('awesome') is Proc


# HTML Processor tests


@pytest.mark.parametrize('old,new,use', [
    (None, None, False),
    (None, 'index.html', True),
    ('index.html', None, False),
    ('index.htm', 'index.html', True),
    ('index.html', 'main.html', False),
    ('index.htm', 'main.html', False),
])
def test_is_entry_point(old, new, use):
    assert mod.HtmlProcessor.is_entry_point(new, old) is use
