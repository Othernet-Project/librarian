import mock

import librarian.routes.content as mod

from ..helpers import strip_wrappers


@mock.patch.object(mod, 'request')
@mock.patch.object(mod, 'i18n_url')
@mock.patch.object(mod, 'open_archive')
def test_remove(open_archive, i18n_url, request):
    remove_content = strip_wrappers(mod.remove_content)
    i18n_url.side_effect = lambda x, **y: x

    archive = mock.Mock()
    archive.remove_from_archive.return_value = []
    open_archive.return_value = archive

    mocked_content = mock.Mock()
    mocked_content.md5 = 'foo'

    ret = remove_content(mocked_content)
    archive.remove_from_archive.assert_called_once_with([mocked_content.md5])
    request.app.exts.cache.invalidate.assert_called_once_with(prefix='content')
    assert ret['status'] == 'success'
