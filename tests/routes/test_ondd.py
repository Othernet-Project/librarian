import mock

import librarian.routes.ondd as mod


@mock.patch.object(mod, '_')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Settings, 'request')
def test_settings_form_valid(request, exts, i18n_url, gettext):
    route = mod.Settings()
    route.form = mock.Mock()
    ret = route.form_valid()
    data = dict(ondd=route.form.processed_data)
    exts.setup.append.assert_called_once_with(data)
    i18n_url.assert_called_once_with('dashboard:main')
    assert ret == dict(form=route.form,
                       message=gettext.return_value,
                       redirect_url=i18n_url.return_value)
