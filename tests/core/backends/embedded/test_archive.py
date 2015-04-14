import mock

import librarian.core.backends.embedded as backend_pkg
mocked_backend = mock.MagicMock()
setattr(backend_pkg, 'backend', mocked_backend)
import librarian.core.backends.embedded.archive as mod

db = mocked_backend.storage

MOD = 'librarian.core.backends.embedded.archive'


@mock.patch(MOD + '.os')
@mock.patch(MOD + '.get_zip_path')
def test_remove_silent_failure(get_zip_path, os):
    # FIXME: This needs to be an integration test for full cov
    get_zip_path.return_value = 'foo'
    os.unlink.side_effect = [OSError, None, None]  # first file fails
    ret = mod.remove_from_archive(['foo', 'bar', 'baz'])
    # Deletes three items even though first one fails
    db.Delete.assert_any_calls('zipballs', where="md5 in (?, ?, ?)")
    assert ret == ['foo']


@mock.patch(MOD + '.os')
@mock.patch(MOD + '.get_zip_path')
def test_remove_failure_when_path_is_none(get_zip_path, os):
    # FIXME: This needs to be an integration test for full cov
    get_zip_path.return_value = None
    try:
        ret = mod.remove_from_archive(['foo', 'bar', 'baz'])
    except Exception:
        assert False, 'Expected not to raise'
    db.Delete.assert_any_calls('zipballs', where="md5 in (?, ?, ?)")
    assert ret == ['foo', 'bar', 'baz']


def test_needs_formatting():
    # FIXME: This needs to be an integration test for full cov
    db.result.keep_formatting = True
    ret = mod.needs_formatting('foo')
    assert db.query.called
    assert ret is False
    db.result.keep_formatting = False
    ret = mod.needs_formatting('foo')
    assert ret is True
