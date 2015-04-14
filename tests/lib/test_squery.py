import mock

from librarian.lib import squery as mod

MOD = mod.__name__


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_connection_object_connects(sqlite3):
    """ Connection object starts a connection """
    conn = mod.Connection('foo.db')
    sqlite3.connect.assert_called_once_with(
        'foo.db', detect_types=sqlite3.PARSE_DECLTYPES)
    assert conn._conn.isolation_level is None
    conn._conn.cursor().execute.assert_called_once_with(
        'PRAGMA journal_mode=WAL;')


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_connection_repr(*ignored):
    """ Connection object has human-readable repr """
    conn = mod.Connection('foo.db')
    assert repr(conn) == "<Connection path='foo.db'>"


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_connection_object_remebers_dbpath(sqlite3):
    """ Connection object can remember the database path """
    conn = mod.Connection('foo.db')
    assert conn.path == 'foo.db'


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_connection_has_sqlite3_connection_api(sqlite3):
    """ Connection object exposes sqlite3.Connection methods and props """
    conn = mod.Connection('foo.db')
    assert conn.cursor == sqlite3.connect().cursor
    assert conn.isolation_level == sqlite3.connect().isolation_level


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_connection_close(sqlite3):
    """ Connection object commits before closing """
    conn = mod.Connection('foo.db')
    conn.close()
    assert sqlite3.connect().commit.called
    assert sqlite3.connect().close.called


@mock.patch(MOD + '.sqlite3', autospec=True)
def test_can_set_attributes_on_underlying_connection(sqlite3):
    """ Attributes set on the Connection instance are mirrored correctly """
    conn = mod.Connection('foo.db')
    conn.isolation_level = None
    assert conn.isolation_level == conn._conn.isolation_level
    conn.isolation_level = 'EXCLUSIVE'
    assert conn.isolation_level == conn._conn.isolation_level


@mock.patch(MOD + '.sqlite3')
def test_db_connect(sqlite3):
    mod.Database.connect('foo.db')
    sqlite3.connect.assert_called_once_with(
        'foo.db', detect_types=sqlite3.PARSE_DECLTYPES)


@mock.patch(MOD + '.sqlite3')
def test_db_uses_dbdict(sqlite3):
    """ The database will use a dbdict_factory for all rows """
    conn = mod.Database.connect('foo.db')
    assert conn.row_factory == mod.Row


@mock.patch(MOD + '.sqlite3')
def test_init_db_with_connection(*ignored):
    """ Database object is initialized with a connection """
    conn = mock.Mock()
    db = mod.Database(conn)
    assert db.conn == conn


@mock.patch(MOD + '.sqlite3')
def test_get_cursor(*ignored):
    """ Obtaining curor should return connection's cursor object """
    db = mod.Database(mock.Mock())
    cur = db.cursor
    assert cur == db.conn.cursor.return_value


@mock.patch(MOD + '.sqlite3')
def test_get_curor_only_retrieved_once(sqlite3):
    """ Cursor is only retrieved once """
    db = mod.Database(mock.Mock())
    db.cursor
    db.cursor
    assert db.conn.cursor.call_count == 1


@mock.patch(MOD + '.sqlite3')
def test_convert_sqlbuilder_class_to_repr(*ignored):
    """ When sqlbuilder object is passed as query, it's converted to repr """
    db = mod.Database(mock.Mock())
    select = mock.Mock(spec=mod.Select)
    select.serialize.return_value = 'SELECT * FROM foo;'
    sql = db._convert_query(select)
    assert sql == select.serialize.return_value


@mock.patch(MOD + '.sqlite3')
def test_convert_string_query(*ignored):
    """ When raw SQL sting is passed, it's not conveted """
    s = 'foobar'
    db = mod.Database(mock.Mock())
    sql = db._convert_query(s)
    assert s is sql


@mock.patch(MOD + '.sqlite3')
def test_query(sqlite3):
    """ query() should execute a database query """
    db = mod.Database(mock.Mock())
    db.query('SELECT * FROM foo;')
    db.cursor.execute.assert_called_once_with('SELECT * FROM foo;', {})


@mock.patch(MOD + '.sqlite3')
@mock.patch.object(mod.Database, '_convert_query')
def test_query_converts(*ignored):
    """ Querying will convert the query """
    db = mod.Database(mock.Mock())
    qry = mock.Mock()
    db.query(qry)
    db._convert_query.assert_called_once_with(qry)
    db.cursor.execute.assert_called_once_with(db._convert_query(), {})


@mock.patch(MOD + '.sqlite3')
def test_query_params(sqlite3):
    """ Query converts positional arguments to params list """
    db = mod.Database(mock.Mock())
    db.query('SELECT * FROM foo WHERE bar = ?;', 12)
    db.cursor.execute.assert_called_once_with(
        'SELECT * FROM foo WHERE bar = ?;', (12,))


@mock.patch(MOD + '.sqlite3')
def test_query_keyword_params(sqlite3):
    """ Query converts keyword params into dict """
    db = mod.Database(mock.Mock())
    db.query('SELECT * FROM foo WHERE bar = :bar;', bar=12)
    db.cursor.execute.assert_called_once_with(
        'SELECT * FROM foo WHERE bar = :bar;', {'bar': 12})


@mock.patch(MOD + '.sqlite3')
def test_execute_alias(sqlite3):
    """ Instace has execute() alias for cursor.execute() """
    db = mod.Database(mock.Mock())
    db.execute('SELECT * FROM foo WHERE bar = ?;', (12,))
    db.cursor.execute.assert_called_once_with(
        'SELECT * FROM foo WHERE bar = ?;', (12,))


@mock.patch(MOD + '.sqlite3')
def test_executemany_alias(sqlite3):
    """ Instance has executemany() alias for cursor.executemany() """
    db = mod.Database(mock.Mock())
    db.executemany('INSERT INTO foo VALUES (?, ?);', [(1, 2), (3, 4)])
    db.cursor.executemany.assert_called_once_with(
        'INSERT INTO foo VALUES (?, ?);', [(1, 2), (3, 4)])


@mock.patch(MOD + '.sqlite3')
def test_executescript_alias(sqlite3):
    """ Instace has executescript() alias for cursor.executescript() """
    db = mod.Database(mock.Mock())
    db.executescript('SELECT * FROM foo;')
    db.cursor.executescript.assert_called_once_with('SELECT * FROM foo;')


@mock.patch(MOD + '.sqlite3')
def test_commit_alias(sqlite3):
    """ Instance has commit() alias for connection.commit() """
    db = mod.Database(mock.Mock())
    db.commit()
    assert db.conn.commit.called


@mock.patch(MOD + '.sqlite3')
def test_rollback_alias(sqlite3):
    """ Instance has rollback() alias for connection.rollback() """
    db = mod.Database(mock.Mock())
    db.rollback()
    assert db.conn.rollback.called
    assert db.conn.commit.called


@mock.patch(MOD + '.sqlite3')
def test_refresh_table_stats(*ignored):
    """ Instance can call ANALYZE """
    db = mod.Database(mock.Mock())
    db.refresh_table_stats()
    db.cursor.execute.assert_called_once_with('ANALYZE sqlite_master;')


@mock.patch(MOD + '.sqlite3')
def test_acquire_lock(*ignored):
    """ Instance has a method for acquiring exclusive lock """
    db = mod.Database(mock.Mock())
    db.acquire_lock()
    db.cursor.execute.assert_called_once_with('BEGIN EXCLUSIVE;')


@mock.patch(MOD + '.sqlite3')
def test_results(*ignored):
    """ Results property gives access to cursor.fetchall() results """
    db = mod.Database(mock.Mock())
    res = db.results
    assert db.cursor.fetchall.called
    assert res == db.cursor.fetchall.return_value


@mock.patch(MOD + '.sqlite3')
def test_result(*ignored):
    """ Result property gives access to cursor.fetchone() resutls """
    db = mod.Database(mock.Mock())
    res = db.result
    assert db.cursor.fetchone.called
    assert res == db.cursor.fetchone.return_value


@mock.patch(MOD + '.sqlite3')
def test_transaction(*ignored):
    """ Instance has a transaction context manager """
    db = mod.Database(mock.Mock())
    with db.transaction() as cur:
        db.cursor.execute.assert_called_once_with('BEGIN;')
        assert cur == db.cursor
    assert db.conn.commit.called


@mock.patch(MOD + '.sqlite3')
def transaction_rollback(*ignored):
    """ Transactions rolls back on exception """
    db = mod.Database(mock.Mock())
    try:
        with db.transaction():
            raise RuntimeError()
        assert False, 'Expected to raise'
    except RuntimeError:
        assert db.conn.rollback.called


@mock.patch(MOD + '.sqlite3')
def test_transaction_silent_rollback(*ignored):
    """ Transaction silently rolled back if silent flag is passed """
    db = mod.Database(mock.Mock())
    try:
        with db.transaction(silent=True):
            raise RuntimeError()
        assert db.conn.rollback.called
    except RuntimeError:
        assert False, 'Expected not to raise'


@mock.patch(MOD + '.sqlite3')
def test_database_repr(*ignored):
    """ Transaction has a human-readable repr """
    conn = mock.Mock()
    conn.path = 'foo.db'
    db = mod.Database(conn)
    assert repr(db) == "<Database connection='foo.db'>"


def test_row_factory():
    """ Factory should create a tuple w/ subscript and attr access """
    # We are doing this test without mocking because of the squery.Row subclass
    # of sqlite3.Row, which is implemented in C and not particularly friendly
    # to mock objects.
    conn = mod.Database.connect(':memory:')
    db = mod.Database(conn)
    db.query('create table foo (bar integer);')
    db.query('insert into foo values (1);')
    db.query('select * from foo;')
    res = db.result
    assert res.get('bar') == res.bar == res[0] == res['bar'] == 1
    assert res.keys() == ['bar']
    assert 'bar' in res
    assert res.get('missing', 'def') == 'def'


def test_row_factory_unicode_key():
    """ Factory should handle unicode keys correctly when using .get() """
    conn = mod.Database.connect(':memory:')
    db = mod.Database(conn)
    db.query('create table foo (bar integer);')
    db.query('insert into foo values (1);')
    db.query('select * from foo;')
    res = db.result
    assert res.get(u'bar', 'def') == 1


@mock.patch(MOD + '.sqlite3')
@mock.patch(MOD + '.print', create=True)
def test_debug_printing(mock_print, *ignored):
    db = mod.Database(mock.Mock(), debug=False)
    db.query('SELECT * FROM foo;')
    assert mock_print.called is False
    db.debug = True
    db.query('SELECT * FROM foo;')
    mock_print.assert_called_once_with('SQL:', 'SELECT * FROM foo;')


@mock.patch(MOD + '.Database.connect')
def test_get_databases_connects(db_connect):
    """ When database name is passed as string, connection is made """
    mod.get_databases({'foo': 'foo.db'})
    db_connect.assert_called_once_with('foo.db')


@mock.patch(MOD + '.Database')
def test_get_databases_does_not_connect_if_connection_is_passed(Database):
    """ When connection object is passed, connection is not made """
    mod.get_databases({})
    assert not Database.connect.called
