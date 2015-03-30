import mock

import librarian.routes.content as mod

from ..helpers import strip_wrappers

MOD = 'librarian.routes.content'


@mock.patch(MOD + '.redirect')
@mock.patch(MOD + '.i18n')
@mock.patch('librarian.core.archive.remove_from_archive')
def test_remove(remove_from_archive, i18n, redirect):
    remove_content = strip_wrappers(mod.remove_content)
    i18n.i18n_path.side_effect = lambda x: x
    remove_from_archive.return_value = []
    ret = remove_content('foo')
    remove_from_archive.assert_called_once_with(['foo'])
    assert ret is None
    redirect.assert_called_once_with('/')


@mock.patch(MOD + '.redirect')
@mock.patch(MOD + '.i18n')
@mock.patch('librarian.core.archive.remove_from_archive')
def test_remove_failed(remove_from_archive, i18n, redirect):
    remove_content = strip_wrappers(mod.remove_content)
    i18n.i18n_path.side_effect = lambda x: x
    remove_from_archive.return_value = ['foo']
    ret = remove_content('foo')
    assert ret == {'redirect': '/'}
    assert not redirect.called


@mock.patch(MOD + '.downloads')
@mock.patch(MOD + '.abort')
def test_content_file_404_on_missing_zipfile_content(abort, downloads):
    from librarian.core.downloads import ContentError
    downloads.get_file.side_effect = ContentError('foo', 'bar')
    downloads.ContentError = ContentError
    abort.side_effect = ValueError  # this is just there to simulate real abort
    try:
        mod.content_file('foo', 'bar')
    except ValueError:
        abort.assert_called_once_with(404)
    except Exception:
        assert False, 'Expected not to raise'
