import mock
import pytest

import librarian.core.downloads as mod


@mock.patch.object(mod.scandir, 'scandir')
def test_get_downloads(scandir):
    filename = 'file.zip'
    file_path = '/path/' + filename
    mocked_entry = mock.Mock()
    mocked_entry.name = filename
    mocked_entry.path = file_path
    scandir.return_value = [mocked_entry]
    dls = list(mod.get_downloads('/path', 'zip'))
    assert len(dls) == 1
    assert dls[0] == file_path


@mock.patch.object(mod.os, 'stat')
def test_order_downloads(stat):
    first = 1431336679.6701245
    second = 1431338879.6701245
    third = 1531338879.6701245
    timestamps = {3: third, 1: first, 2: second}

    def mocked_stat(path):
        m = mock.Mock()
        m.st_mtime = timestamps[path]
        return m

    stat.side_effect = mocked_stat
    expected = [(1, first), (2, second), (3, third)]
    assert mod.order_downloads([2, 1, 3]) == expected


@mock.patch.object(mod.os, 'unlink')
def test_safe_remove_success(unlink):
    file_path = '/path/file.zip'
    assert mod.safe_remove(file_path)
    unlink.assert_called_once_with(file_path)


@mock.patch.object(mod.os, 'unlink')
def test_safe_remove_fail(unlink):
    file_path = '/path/file.zip'
    unlink.side_effect = OSError()
    assert not mod.safe_remove(file_path)
    unlink.assert_called_once_with(file_path)


def test_remove_downloads_fail():
    with pytest.raises(TypeError):
        mod.remove_downloads('/path/dir')


@mock.patch.object(mod, 'safe_remove')
@mock.patch.object(mod.zipballs, 'get_zip_path')
def test_remove_downloads_exact(get_zip_path, safe_remove):
    file_path = '/path/file.zip'
    get_zip_path.return_value = file_path
    safe_remove.return_value = True
    assert mod.remove_downloads('/root', content_ids=['md5']) == 1
    safe_remove.assert_called_once_with(file_path)
    get_zip_path.assert_called_once_with('md5', '/root')


@mock.patch.object(mod, 'safe_remove')
@mock.patch.object(mod, 'get_downloads')
def test_remove_downloads_all(get_downloads, safe_remove):
    file_path = '/path/file.zip'
    get_downloads.return_value = [file_path]
    safe_remove.return_value = True
    assert mod.remove_downloads('/root', extension='zip') == 1
    safe_remove.assert_called_once_with(file_path)
    get_downloads.assert_called_once_with('/root', 'zip')
