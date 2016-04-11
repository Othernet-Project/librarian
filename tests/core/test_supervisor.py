import functools

import pytest

try:
    from unittest import mock
except ImportError:
    import mock


from librarian.core import supervisor as mod


MOD = mod.__name__


def patched_supervisor_init(fn):
    @mock.patch.object(mod, 'ext_container')
    @mock.patch.object(mod.Supervisor, 'configure')
    @mock.patch.object(mod.Supervisor, 'configure_logger')
    @mock.patch.object(mod.Supervisor, 'load_components')
    @mock.patch.object(mod.Supervisor, 'handle_interrupt')
    @mock.patch.object(mod.Supervisor, 'finalize')
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


default_components = [
    'librarian.core.contrib.assets',
    'librarian.core.contrib.system',
    'librarian.core.contrib.commands',
    'librarian.core.contrib.databases',
    'librarian.core.contrib.sessions',
    'librarian.core.contrib.auth',
    'librarian.core.contrib.i18n',
    'librarian.core.contrib.cache',
    'librarian.core.contrib.tasks',
    'librarian.core.contrib.templates',
    'librarian',  # <-- must include root
]


def test_root_package_attribute():
    """
    ROOT_PKG attribute always poits to the package supervisor lives in, and in
    this case, it's 'librarian'.
    """
    assert mod.Supervisor.ROOT_PKG == 'librarian'


@patched_supervisor_init
def test_get_components_requres_no_special_config(*ignroed):
    s = mod.Supervisor('foo')
    s.config = {}
    s.get_component_list()
    assert True, 'Should not raise'


@patched_supervisor_init
def test_get_component_list_minimal(*ignored):
    s = mod.Supervisor('foo')
    s.config = {}
    ret = s.get_component_list()
    assert ret == default_components


@patched_supervisor_init
def test_get_components_does_not_fail_on_weird_value(*ignroed):
    s = mod.Supervisor('foo')
    s.config = {'app.components': ''}
    ret = s.get_component_list()
    assert ret == default_components


@patched_supervisor_init
def test_core_override_excludes_core_components(*ignored):
    s = mod.Supervisor('foo')
    s.config = {'app.core_override': True}
    ret = s.get_component_list()
    assert ret == ['librarian']


@patched_supervisor_init
@mock.patch(MOD + '.PubSub')
def test_install_hook(*ignored):
    s = mod.Supervisor('foo')
    mock_fn = mock.Mock()
    s.install_hook('foo', mock_fn)
    s.exts.events.subscribe.assert_called_once_with('foo', mock_fn)


@patched_supervisor_init
@mock.patch(MOD + '.PubSub')
def test_install_hook_initialize(*ignored):
    s = mod.Supervisor('foo')
    mock_fn = mock.Mock()
    s.install_hook(s.INITIALIZE, mock_fn, 'mymod')
    s.exts.events.subscribe.assert_called_once_with(s.INITIALIZE, mock_fn)
    s.exts.events.publish.assert_called_once_with(s.INITIALIZE, s,
                                                  scope='mymod')


@patched_supervisor_init
@mock.patch(MOD + '.PubSub')
def test_install_hook_initialize_with_no_mod(*ignored):
    s = mod.Supervisor('foo')
    mock_fn = mock.Mock()
    with pytest.raises(TypeError):
        s.install_hook(s.INITIALIZE, mock_fn)


@patched_supervisor_init
@mock.patch(MOD + '.PubSub')
def test_install_routes(*ignored):
    s = mod.Supervisor('foo')
    s.config = {}
    s.app = mock.Mock()
    mock_route_fn = mock.Mock()
    mock_fn = mock.Mock()
    mock_route_fn.return_value = [
        ('foobar', mock_fn, 'GET', '/', {}),
        ('barbaz', mock_fn, 'POST', '/other', {'foo': 'bar'}),
    ]
    s.install_routes(mock_route_fn)
    mock_route_fn.assert_called_once_with({})
    s.app.route.asset_has_calls([
        mock.call('/', 'GET', mock_fn, name='foobar'),
        mock.call('/other', 'POST', mock_fn, name='barbaz', foo='bar'),
    ])


@patched_supervisor_init
@mock.patch(MOD + '.PubSub')
def test_install_plugin(*ignored):
    s = mod.Supervisor('foo')
    s.app = mock.Mock()
    mock_plugin = mock.Mock()
    s.install_plugin(mock_plugin)
    mock_plugin.assert_called_once_with(s)
    s.app.install.assert_called_once_with(mock_plugin.return_value)
