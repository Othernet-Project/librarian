import mock

import librarian.core.archive as mod

MOD = 'librarian.core.archive'


@mock.patch(MOD + '.os')
@mock.patch(MOD + '.request')
@mock.patch(MOD + '.get_zip_path')
def test_remove_silent_failure(get_zip_path, request, os):
    # FIXME: This needs to be an integration test for full cov
    get_zip_path.return_value = 'foo'
    os.unlink.side_effect = [OSError, None, None]  # first file fails
    ret = mod.remove_from_archive(['foo', 'bar', 'baz'])
    # Deletes three items even though first one fails
    request.db.Delete.assert_any_calls('zipballs', where="md5 in (?, ?, ?)")
    assert ret == ['foo']


@mock.patch(MOD + '.os')
@mock.patch(MOD + '.request')
@mock.patch(MOD + '.get_zip_path')
def test_remove_failure_when_path_is_none(get_zip_path, request, os):
    # FIXME: This needs to be an integration test for full cov
    get_zip_path.return_value = None
    try:
        ret = mod.remove_from_archive(['foo', 'bar', 'baz'])
    except Exception:
        assert False, 'Expected not to raise'
    request.db.Delete.assert_any_calls('zipballs', where="md5 in (?, ?, ?)")
    assert ret == ['foo', 'bar', 'baz']


@mock.patch(MOD + '.request')
def test_needs_formatting(request):
    # FIXME: This needs to be an integration test for full cov
    request.db = db = mock.Mock()
    db.result.keep_formatting = True
    ret = mod.needs_formatting('foo')
    assert db.query.called
    assert ret is False
    db.result.keep_formatting = False
    ret = mod.needs_formatting('foo')
    assert ret is True
