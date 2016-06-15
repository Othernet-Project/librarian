try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import mock

import librarian.routes.auth as mod


# Test login route handler


@mock.patch.object(mod.Login, 'perform_redirect')
@mock.patch.object(mod.Login, 'request')
def test_login_form_valid(request, perform_redirect):
    route = mod.Login()
    assert route.form_valid() is None
    request.user.options.process.assert_called_once_with('language')
    perform_redirect.assert_called_once_with()


# Test logout route handler


@mock.patch.object(mod.Logout, 'perform_redirect')
@mock.patch.object(mod.Logout, 'request')
def test_logout_get(request, perform_redirect):
    route = mod.Logout()
    assert route.get() == ''
    request.user.logout.assert_called_once_with()
    perform_redirect.assert_called_once_with()


# Test reset password route handler


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'template')
@mock.patch.object(mod.User, 'set_password')
@mock.patch.object(mod.PasswordReset, 'request')
def test_reset_password_form_valid(request, set_password, template, i18n_url,
                                   lazy_gettext):
    request.user.is_authenticated = False
    route = mod.PasswordReset()
    route.form = mock.Mock()
    route.form.processed_data = {'username': 'usr', 'password1': 'pwd'}
    resp = route.form_valid()
    assert isinstance(resp, mod.PasswordReset.HTTPResponse)
    set_password.assert_called_once_with('usr', 'pwd')


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'template')
@mock.patch.object(mod.User, 'set_password')
@mock.patch.object(mod.PasswordReset, 'request')
def test_reset_password_form_valid_authenticated(request, set_password,
                                                 template, i18n_url, _):
    request.user.is_authenticated = True
    route = mod.PasswordReset()
    route.form = mock.Mock()
    route.form.processed_data = {'username': 'usr', 'password1': 'pwd'}
    route.form_valid()
    request.user.logout.assert_called_once_with()


# Test emergency reset route handler


@mock.patch.object(mod.EmergencyReset, 'request')
@mock.patch.object(mod.EmergencyReset, 'abort')
@mock.patch.object(mod.os.path, 'isfile')
def test_emergency_reset_read_token_file_not_found(isfile, abort, request):
    isfile.return_value = False
    route = mod.EmergencyReset()
    route.read_token_file()
    abort.assert_called_once_with(404)


@mock.patch.object(mod.EmergencyReset, 'request')
@mock.patch.object(mod.EmergencyReset, 'abort')
@mock.patch.object(mod.os.path, 'isfile')
@mock.patch.object(builtins, 'open')
def test_emergency_reset_read_token_file_empty(open_fn, isfile, abort,
                                               request):
    isfile.return_value = True
    # set up mocked empty file object
    mocked_file = mock.Mock()
    mocked_file.read.return_value = ''
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_file
    open_fn.return_value = ctx_manager
    # perform test
    route = mod.EmergencyReset()
    with mock.patch.object(route, 'config') as config:
        route.read_token_file()
        abort.assert_called_once_with(404)
        open_fn.assert_called_once_with(config.get.return_value, 'r')


@mock.patch.object(mod.EmergencyReset, 'request')
@mock.patch.object(mod.EmergencyReset, 'abort')
@mock.patch.object(mod.os.path, 'isfile')
@mock.patch.object(builtins, 'open')
def test_emergency_reset_read_token_file(open_fn, isfile, abort, request):
    isfile.return_value = True
    # set up mocked empty file object
    mocked_file = mock.Mock()
    mocked_file.read.return_value = 'token'
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_file
    open_fn.return_value = ctx_manager
    # perform test
    route = mod.EmergencyReset()
    assert route.read_token_file() == 'token'
    assert not abort.called


@mock.patch.object(mod.User, 'generate_reset_token')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_get_reset_token(request, generate_reset_token):
    route = mod.EmergencyReset()
    # test case of GET request
    request.method = 'GET'
    assert route.get_reset_token() == generate_reset_token.return_value
    # test case of POST request
    request.method = 'POST'
    assert route.get_reset_token() == request.params.get.return_value


@mock.patch.object(mod.EmergencyReset, 'request')
@mock.patch.object(mod, 'exts')
def test_emergency_reset_clear_auth_databases(exts, request):
    route = mod.EmergencyReset()
    route.clear_auth_databases()
    db = exts.databases.librarian
    db.Delete.assert_any_call('users')
    db.execute.assert_any_call(db.Delete.return_value)
    db.Delete.assert_any_call('sessions')
    db.execute.assert_any_call(db.Delete.return_value)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.User, 'create')
@mock.patch.object(mod.EmergencyReset, 'get_reset_token')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_recreate_user(request, get_reset_token, create, exts):
    route = mod.EmergencyReset()
    route.recreate_user('usr', 'pwd')
    create.assert_called_once_with('usr',
                                   'pwd',
                                   is_superuser=True,
                                   db=exts.databases.librarian,
                                   reset_token=get_reset_token.return_value)


@mock.patch.object(mod.EmergencyReset, 'get_reset_token')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_get_context(request, get_reset_token):
    route = mod.EmergencyReset()
    ctx = route.get_context()
    assert ctx['reset_token'] == get_reset_token.return_value


@mock.patch.object(builtins, 'super')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod.EmergencyReset, 'read_token_file')
@mock.patch.object(mod.EmergencyReset, 'redirect')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_get_authenticated(request, redirect, read_token_file,
                                           i18n_url, super_fn):
    request.user.is_authenticated = True
    route = mod.EmergencyReset()
    route.get()
    read_token_file.assert_called_once_with()
    redirect.assert_called_once_with(i18n_url.return_value)
    assert not super_fn.called


@mock.patch.object(builtins, 'super')
@mock.patch.object(mod.EmergencyReset, 'read_token_file')
@mock.patch.object(mod.EmergencyReset, 'redirect')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_get_not_authenticated(request, redirect,
                                               read_token_file, super_fn):
    request.user.is_authenticated = False
    route = mod.EmergencyReset()
    route.get()
    read_token_file.assert_called_once_with()
    assert not redirect.called
    assert super_fn.called


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'template')
@mock.patch.object(mod.EmergencyReset, 'recreate_user')
@mock.patch.object(mod.EmergencyReset, 'clear_auth_databases')
@mock.patch.object(mod.EmergencyReset, 'request')
def test_emergency_reset_form_valid(request, clear_auth_databases,
                                    recreate_user, template, lazy_gettext):
    route = mod.EmergencyReset()
    route.form = mock.Mock()
    route.form.processed_data = {'username': 'usr', 'password1': 'pwd'}
    resp = route.form_valid()
    clear_auth_databases.assert_called_once_with()
    recreate_user.assert_called_once_with('usr', 'pwd')
    assert isinstance(resp, mod.EmergencyReset.HTTPResponse)
