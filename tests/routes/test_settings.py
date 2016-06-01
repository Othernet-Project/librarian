import mock

import librarian.routes.settings as mod


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Settings, 'request')
def test_settings_get_form_factory(request, exts):
    route = mod.Settings()
    assert route.get_form_factory() == exts.settings.get_form.return_value


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Settings, 'request')
def test_settings_get_context(request, exts):
    route = mod.Settings()
    ret = route.get_context()
    assert ret['groups'] == exts.settings.groups


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Settings, 'request')
def test_settings_form_valid(request, exts, i18n_url, gettext):
    route = mod.Settings()
    route.form = mock.Mock()
    assert route.form_valid() == dict(message=gettext.return_value,
                                      redirect_url=i18n_url.return_value)
    exts.setup.append.assert_called_once_with(route.form.processed_data)
    exts.events.publish.assert_called_once_with('SETTINGS_SAVED',
                                                route.form.processed_data)
    i18n_url.assert_called_once_with('dashboard:main')
