import mock

import librarian.routes.ondd as mod


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Status, 'request')
def test_status_get(request, exts):
    route = mod.Status()
    route.config = {'ondd.snr_min': 0.1,
                    'ondd.snr_max': 0.8}
    assert route.get() == dict(status=exts.ondd.get_status.return_value,
                               SNR_MIN=0.1,
                               SNR_MAX=0.8)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.FileList, 'request')
def test_filelist_get(request, exts):
    route = mod.FileList()
    assert route.get() == dict(files=exts.ondd.get_transfers.return_value)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.CacheStatus, 'request')
def test_cache_status_get_default(request, exts):
    route = mod.CacheStatus()
    route.config = {'ondd.cache_quota': 1}
    exts.cache.get.return_value = None
    default = dict(total=1, free=1, used=0, alert=False)
    assert route.get() == dict(cache_status=default)
    exts.cache.get.assert_called_once_with('ondd.cache')


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.CacheStatus, 'request')
def test_cache_status_get(request, exts):
    route = mod.CacheStatus()
    assert route.get() == dict(cache_status=exts.cache.get.return_value)
    exts.cache.get.assert_called_once_with('ondd.cache')


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
