import mock

import librarian.utils.setup as mod


@mock.patch.object(mod.Setup, 'auto_configure')
@mock.patch.object(mod.Setup, 'load')
def test_setup_init_already_completed(load, auto_configure):
    load.return_value = {'some': 'data', 'completed': True}
    setup = mod.Setup('setup.json')
    assert setup.data == {'some': 'data', 'completed': True}
    assert not auto_configure.called


@mock.patch.object(mod.Setup, 'auto_configure')
@mock.patch.object(mod.Setup, 'load')
def test_setup_init_not_completed(load, auto_configure):
    load.return_value = None
    auto_configure.return_value = {'auto': 'configured'}
    setup = mod.Setup('setup.json')
    assert setup.data == {'auto': 'configured'}
    auto_configure.assert_called_once_with()


@mock.patch.object(mod.Setup, 'load')
def test_setup_data_access(load):
    load.return_value = {'some': 'data'}
    setup = mod.Setup('setup.json')

    assert setup['some'] == 'data'
    assert setup.get('some') == 'data'
    assert setup.get('invalid', 1) == 1


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.Setup, '__init__')
def test_load_does_not_exist(init, exists):
    exists.return_value = False
    init.return_value = None
    setup = mod.Setup()
    setup.setup_file = '/path/to/setup.json'
    assert setup.load() == {}
    exists.assert_called_once_with('/path/to/setup.json')


@mock.patch.object(mod.json, 'load')
@mock.patch('__builtin__.open')
@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.Setup, '__init__')
def test_load_invalid_config(init, exists, f_open, json_load):
    exists.return_value = True
    init.return_value = None
    setup = mod.Setup()
    setup.setup_file = '/path/to/setup.json'

    mocked_file = mock.Mock()
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_file
    f_open.return_value = ctx_manager

    json_load.side_effect = ValueError()

    assert setup.load() == {}

    exists.assert_called_once_with('/path/to/setup.json')
    json_load.assert_called_once_with(mocked_file)


@mock.patch.object(mod.json, 'dump')
@mock.patch('__builtin__.open')
@mock.patch.object(mod.Setup, '__init__')
def test_save_config(init, f_open, json_dump):
    init.return_value = None
    setup = mod.Setup()
    setup.setup_file = '/path/to/setup.json'
    setup.data = {'auto': 'configured'}

    mocked_file = mock.Mock()
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_file
    f_open.return_value = ctx_manager

    setup.append({'setup': 'result', 'another': 1})

    merged_data = {'auto': 'configured',
                   'setup': 'result',
                   'another': 1}
    json_dump.assert_called_once_with(merged_data, mocked_file)
