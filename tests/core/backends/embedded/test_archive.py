import mock
import pytest

from librarian.lib.squery import Database

import librarian.core.backends.embedded.archive as mod


MOD = mod.__name__


@pytest.fixture
def archive():
    mocked_db = mock.Mock()
    mocked_db.sqlin = Database.sqlin
    return mod.EmbeddedArchive(mocked_db, content_dir='unimportant')


def mock_cursor(func):
    def _mock_cursor(archive, *args, **kwargs):
        mocked_cursor = mock.Mock()
        ctx_manager = mock.MagicMock()
        ctx_manager.__enter__.return_value = mocked_cursor
        archive.db.transaction.return_value = ctx_manager
        return func(mocked_cursor, archive, *args, **kwargs)
    return _mock_cursor


@mock_cursor
def test_remove_meta_from_db(cursor, archive):
    hashes = ['foo', 'bar', 'baz']
    cursor.rowcount = len(hashes)
    sql = 'proper delete query'
    archive.db.Delete.return_value = sql

    result = archive.remove_meta_from_db(hashes)

    delete_calls = [
        mock.call('zipballs', where="md5 IN (?, ?, ?)"),
        mock.call('taggings', where="md5 IN (?, ?, ?)")
    ]
    archive.db.Delete.assert_has_calls(delete_calls)

    query_calls = [
        mock.call(sql, *hashes),
        mock.call(sql, *hashes)
    ]
    archive.db.query.assert_has_calls(query_calls)

    assert result == len(hashes)


def test_needs_formatting(archive):
    # FIXME: This needs to be an integration test for full cov
    archive.db.result.keep_formatting = True
    ret = archive.needs_formatting('foo')
    assert archive.db.query.called
    assert ret is False
    archive.db.result.keep_formatting = False
    ret = archive.needs_formatting('foo')
    assert ret is True
