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
@mock.patch.object(mod.ResetPassword, 'request')
def test_reset_password_form_valid(request, set_password, template, i18n_url,
                                   lazy_gettext):
    request.user.is_authenticated = False
    route = mod.ResetPassword()
    route.form = mock.Mock()
    route.form.processed_data = {'username': 'usr', 'password1': 'pwd'}
    resp = route.form_valid()
    assert isinstance(resp, mod.ResetPassword.HTTPResponse)
    set_password.assert_called_once_with('usr', 'pwd')


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'template')
@mock.patch.object(mod.User, 'set_password')
@mock.patch.object(mod.ResetPassword, 'request')
def test_reset_password_form_valid_authenticated(request, set_password,
                                                 template, i18n_url, _):
    request.user.is_authenticated = True
    route = mod.ResetPassword()
    route.form = mock.Mock()
    route.form.processed_data = {'username': 'usr', 'password1': 'pwd'}
    route.form_valid()
    request.user.logout.assert_called_once_with()
