import mock

import librarian.routes.content as mod

from ..helpers import strip_wrappers


@mock.patch.object(mod, 'request')
@mock.patch.object(mod, 'redirect')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'open_archive')
def test_remove(open_archive, i18n_url, redirect, request):
    remove_content = strip_wrappers(mod.remove_content)
    i18n_url.side_effect = lambda x, **y: x

    archive = mock.Mock()
    archive.remove_from_archive.return_value = []
    open_archive.return_value = archive

    ret = remove_content('foo')
    archive.remove_from_archive.assert_called_once_with(['foo'])
    assert ret is None
    redirect.assert_called_once_with('content:list')
    request.app.exts.cache.invalidate.assert_called_once_with(prefix='content')
