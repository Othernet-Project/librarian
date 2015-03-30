import mock

import librarian.core.archive as mod

MOD = 'librarian.core.archive'


@mock.patch(MOD + '.os')
@mock.patch(MOD + '.request')
@mock.patch(MOD + '.get_zip_path')
def test_remove_silent_failure(get_zip_path, request, os):
    get_zip_path.return_value = ('foo', 'foo')
    os.unlink.side_effect = [OSError, None, None]  # first file fails
    ret = mod.remove_from_archive(['foo', 'bar', 'baz'])
    # Deletes three items even though first one fails
    request.db.Delete.assert_any_calls('zipballs', where="md5 in (?, ?, ?)")
    assert ret == ['foo']

