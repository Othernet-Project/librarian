try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import mock
import pytest

import librarian.data.setup as mod


@mock.patch.object(mod.Setup, '_update_config')
@mock.patch.object(mod, 'json')
@mock.patch.object(builtins, 'open')
def test_append(open_fn, json, _update_config):
    s = mod.Setup('/setup/path')
    test_data = {'a': 1, 'b': 2}
    s.append(test_data)
    open_fn.assert_called_once_with('/setup/path', 'w')
    mock_file = open_fn.return_value.__enter__.return_value
    json.dump.assert_called_once_with(test_data, mock_file)
    assert _update_config.called
    assert s.items() == test_data.items()


@mock.patch.object(mod, 'exts')
def test__update_config(exts):
    test_data = {'a': 1, 'b': 2}
    s = mod.Setup('path', test_data)
    s._update_config()
    exts.config.update.assert_called_once_with(test_data)


@mock.patch.object(mod.os.path, 'exists')
def test__read_does_not_exist(exists):
    exists.return_value = False
    s = mod.Setup('path')
    s._read()
    assert s._data == {}


@mock.patch.object(builtins, 'open')
@mock.patch.object(mod.os.path, 'exists')
def test__read_failed(exists, open_fn):
    exists.return_value = True
    open_fn.side_effect = IOError()
    s = mod.Setup('path')
    s._read()
    assert s._data == {}
    assert open_fn.called


@mock.patch.object(mod, 'json')
@mock.patch.object(builtins, 'open')
@mock.patch.object(mod.os.path, 'exists')
def test__read_success(exists, open_fn, json):
    exists.return_value = True
    s = mod.Setup('/setup/path')
    s._read()
    assert s._data == json.load.return_value
    open_fn.assert_called_once_with('/setup/path', 'r')
    mock_file = open_fn.return_value.__enter__.return_value
    json.load.assert_called_once_with(mock_file)


@mock.patch.object(mod.Setup, 'append')
def test__auto_configure(append):
    s = mod.Setup('path')
    first = mock.Mock()
    second = mock.Mock()
    s._auto_configurators['first'] = first
    s._auto_configurators['second'] = second
    s._auto_configure()
    append.assert_called_once_with({'first': first.return_value,
                                    'second': second.return_value})


@pytest.mark.parametrize('initial', [{}, {'test': 'data'}])
@mock.patch.object(mod.Setup, '_update_config')
@mock.patch.object(mod.Setup, '_auto_configure')
@mock.patch.object(mod.Setup, '_read')
def test_load(_read, _auto_configure, _update_config, initial):
    s = mod.Setup('path', initial)
    s.load()
    assert _read.called
    if initial:
        assert not _auto_configure.called
    else:
        assert _auto_configure.called
    assert _update_config.called


def test_autoconfigure():
    mod.Setup._auto_configurators = {}
    auto_cfg = mock.Mock()
    mod.Setup.autoconfigure('test', auto_cfg)
    assert mod.Setup._auto_configurators == {'test': auto_cfg}
