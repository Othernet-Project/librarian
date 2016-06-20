try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import StringIO

import mock
import pytest

import librarian.routes.setup as mod


def test_iter_log():
    file_obj = StringIO.StringIO('ignored\nnext\ndata')
    assert list(mod.iter_log(file_obj, 2)) == ['data', 'next\n']


@pytest.mark.parametrize('source,expected', [
    ('test', 100),
    (0, 0),
    (50, 50),
    ('70', 70),
    (None, 100),
])
@mock.patch.object(mod.Diag, 'request')
def test_diag_get_lines(request, source, expected):
    request.params = {'lines': source}
    route = mod.Diag()
    assert route.get_lines() == expected


@mock.patch.object(mod, 'iter_log')
@mock.patch.object(builtins, 'open')
@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.Diag, 'get_lines')
@mock.patch.object(mod.Diag, 'request')
def test_diag_get_log_iterator(request, get_lines, exists, open_fn, iter_log):
    exists.return_value = True
    mocked_file = mock.Mock()
    mocked_file.read.return_value = ''
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_file
    open_fn.return_value = ctx_manager
    route = mod.Diag()
    route.config = {'logging.syslog': '/var/log/messages'}
    assert route.get_log_iterator() == iter_log.return_value
    open_fn.assert_called_once_with('/var/log/messages', 'rt')
    iter_log.assert_called_once_with(mocked_file, get_lines.return_value)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Diag, 'get_log_iterator')
@mock.patch.object(mod.Diag, 'redirect')
@mock.patch.object(mod.Diag, 'request')
def test_diag_get_already_completed(request, redirect, get_log_iterator, exts):
    exts.setup_wizard.is_completed = True
    route = mod.Diag()
    route.get()
    redirect.assert_called_once_with('/')
    assert not get_log_iterator.called


@mock.patch.object(mod, 'has_tuner')
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Diag, 'get_log_iterator')
@mock.patch.object(mod.Diag, 'redirect')
@mock.patch.object(mod.Diag, 'request')
def test_diag_get(request, redirect, get_log_iterator, exts, has_tuner):
    exts.setup_wizard.is_completed = False
    route = mod.Diag()
    assert route.get() == dict(logs=get_log_iterator.return_value,
                               has_tuner=has_tuner.return_value)
    get_log_iterator.assert_called_once_with()
    has_tuner.assert_called_once_with()
    assert not redirect.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Enter, 'request')
def test_enter_get(request, exts):
    route = mod.Enter()
    assert route.get() == exts.setup_wizard.return_value


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Exit, 'perform_redirect')
@mock.patch.object(mod.Exit, 'request')
def test_exit_get(request, perform_redirect, exts):
    route = mod.Exit()
    assert route.get() is None
    exts.setup_wizard.exit.assert_called_once_with()
    perform_redirect.assert_called_once_with()
