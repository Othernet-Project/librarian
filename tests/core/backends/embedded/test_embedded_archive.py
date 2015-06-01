import mock
import pytest

from librarian.lib.squery import Database

import librarian.core.backends.embedded.archive as mod


MOD = mod.__name__


@pytest.fixture
def archive():
    mocked_db = mock.Mock()
    mocked_db.sqlin = Database.sqlin
    return mod.EmbeddedArchive(mocked_db,
                               unpackdir='unpackdir',
                               contentdir='contentdir',
                               spooldir='spooldir',
                               meta_filename='metafile.ext')


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
    cursor.rowcount = 1
    md5 = 'an md5hash'
    sql = 'proper delete query'
    archive.db.Delete.return_value = sql

    assert archive.remove_meta_from_db(md5) == 1

    delete_calls = [
        mock.call('zipballs', where="md5 = ?"),
        mock.call('taggings', where="md5 = ?")
    ]
    archive.db.Delete.assert_has_calls(delete_calls)

    query_calls = [
        mock.call(sql, md5),
        mock.call(sql, md5)
    ]
    archive.db.query.assert_has_calls(query_calls)


@mock_cursor
def test_add_meta_to_db(cursor, archive):
    cursor.rowcount = 1
    delete_sql = 'proper delete query'
    replace_sql = 'proper replace query'
    archive.db.Delete.return_value = delete_sql
    archive.db.Replace.return_value = replace_sql
    metadata = {
        "url": "http://en.wikipedia.org/wiki/Sweden",
        "title": "content title",
        "timestamp": "2014-08-10 20:35:17 UTC",
        "md5": "13b320accaae7ae35b51e79fcebaea05",
        "replaces": "1fa7b8c2430bb75642d062f08f00a115"
    }
    assert archive.add_meta_to_db(metadata) == 1
    archive.db.Replace.assert_called_once_with('zipballs',
                                               cols=archive.db_fields)
    archive.db.Delete.assert_called_once_with('zipballs', where='md5 = ?')
    query_calls = [
        mock.call(replace_sql, **metadata),
        mock.call(delete_sql, metadata['replaces'])
    ]
    archive.db.query.assert_has_calls(query_calls)


def test_needs_formatting(archive):
    # FIXME: This needs to be an integration test for full cov
    archive.db.result.keep_formatting = True
    ret = archive.needs_formatting('foo')
    assert archive.db.query.called
    assert ret is False
    archive.db.result.keep_formatting = False
    ret = archive.needs_formatting('foo')
    assert ret is True
