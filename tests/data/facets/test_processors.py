import mock
import pytest

import librarian.data.facets.processors as mod


@mock.patch.object(mod.Processor, 'get_metadata')
def test_process_file(get_metadata):
    get_metadata.return_value = {'key1': 1, 'key2': 2}
    proc = mod.GenericFacetProcessor()
    expected = {'facet_types': 1, 'key1': 1, 'key2': 2, 'path': '/path/file'}
    assert proc.process_file('/path/file') == expected
    get_metadata.assert_called_once_with('/path/file', False)


@mock.patch.object(mod.Processor, 'get_metadata')
def test_process_file_update(get_metadata):
    get_metadata.return_value = {'key1': 1, 'key2': 2}
    proc = mod.GenericFacetProcessor()
    data = {}
    expected = {'facet_types': 1, 'key1': 1, 'key2': 2, 'path': '/path/file'}
    ret = proc.process_file('/path/file', data=data)
    assert ret is data  # make sure passed in data object is reused
    assert ret == expected  # make sure it's value is what we expect
    get_metadata.assert_called_once_with('/path/file', False)


@mock.patch.object(mod.Processor, 'get_metadata')
def test_process_file_partial(get_metadata):
    proc = mod.GenericFacetProcessor()
    proc.process_file('/path/file', partial=True)
    get_metadata.assert_called_once_with('/path/file', True)


@mock.patch.object(mod.Processor, 'metadata_class')
def test_get_metadata_partial(metadata_class):
    proc = mod.GenericFacetProcessor()
    assert proc.get_metadata('/path/file', partial=True) == {}
    assert not metadata_class.called


def test_get_metadata_no_metadata_class():
    proc = mod.GenericFacetProcessor()
    assert proc.get_metadata('/path/file', partial=False) == {}


@mock.patch.object(mod.Processor, 'metadata_class')
def test_get_metadata_ioerror(metadata_class):
    metadata_class.side_effect = IOError()
    proc = mod.GenericFacetProcessor()
    assert proc.get_metadata('/path/file', partial=False) == {}
    metadata_class.assert_called_once_with(proc.fsal, '/path/file')


@mock.patch.object(mod.ImageFacetProcessor, 'metadata_class')
def test_get_metadata(metadata_class):
    mocked_meta = mock.Mock(width=1, height=2, insignificant=3)
    metadata_class.return_value = mocked_meta
    proc = mod.ImageFacetProcessor()
    proc.get_metadata('/path/file', partial=False) == {'width': 1, 'height': 2}


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


@mock.patch.object(mod.Processor, 'subclasses')
def test_for_path_fail(subclasses):
    subclasses.return_value = []
    with pytest.raises(RuntimeError):
        mod.Processor.for_path('/path/file')


@mock.patch.object(mod.Processor, 'subclasses')
def test_for_path_success(subclasses):
    proc1 = mock.Mock()
    proc2 = mock.Mock()
    proc2.can_process.return_value = False
    proc3 = mock.Mock()
    subclasses.return_value = [proc1, proc2, proc3]
    assert mod.Processor.for_path('/path/file') == [proc1, proc3]
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
def test_use_index(old, new, use):
    assert mod.HtmlFacetProcessor.use_index(new, old) is use
