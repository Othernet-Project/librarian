import mock

from librarian.lib import squery as mod

MOD = mod.__name__


def test_sqlarray():
    assert mod.sqlarray(2) == '(?, ?)'


def test_sqlarray_zero():
    assert mod.sqlarray(0) == ''


def test_sqlarray_list():
    assert mod.sqlarray(['foo', 'bar', 'baz']) == '(?, ?, ?)'


def test_sqlin():
    assert mod.sqlin('foo', 4) == 'foo IN (?, ?, ?, ?)'


def test_sqlin_zero():
    assert mod.sqlin('foo', 0) == ''


def test_from():
    sql = mod.From('foo')
    assert str(sql) == 'FROM foo'


def test_from_table_list():
    sql = mod.From('foo', 'bar')
    assert str(sql) == 'FROM foo , bar'


def test_from_joins():
    sql = mod.From('foo', 'bar', join=mod.From.INNER)
    assert str(sql) == 'FROM foo INNER JOIN bar'


def test_form_add_join():
    sql = mod.From('foo')
    sql.join('bar')
    assert str(sql) == 'FROM foo JOIN bar'


def test_from_add_join_kind():
    sql = mod.From('foo')
    sql.join('bar', mod.From.OUTER)
    assert str(sql) == 'FROM foo OUTER JOIN bar'


def test_from_add_join_natural():
    sql = mod.From('foo')
    sql.join('bar', natural=True)
    assert str(sql) == 'FROM foo NATURAL JOIN bar'


def test_from_add_join_natural_kind():
    sql = mod.From('foo')
    sql.join('bar', mod.From.CROSS, natural=True)
    assert str(sql) == 'FROM foo NATURAL CROSS JOIN bar'


def test_from_add_join_on():
    sql = mod.From('foo')
    sql.join('bar', on='foo.test = bar.footest')
    assert str(sql) == 'FROM foo JOIN bar ON foo.test = bar.footest'


def test_from_add_join_using():
    sql = mod.From('foo')
    sql.join('bar', using='test_id')
    assert str(sql) == 'FROM foo JOIN bar USING (test_id)'


def test_from_add_join_using_multiple():
    sql = mod.From('foo')
    sql.join('bar', using=['test_id', 'something'])
    assert str(sql) == 'FROM foo JOIN bar USING (test_id, something)'


def test_from_add_join_on_and_using():
    sql = mod.From('foo')
    sql.join('bar', on='foo.bar_id = bar.id', using='bar_id')
    assert str(sql) == 'FROM foo JOIN bar ON foo.bar_id = bar.id'


def test_empty_from():
    sql = mod.From()
    assert str(sql) == ''


def test_from_bool():
    sql = mod.From()
    assert not sql
    sql = mod.From('foo')
    assert sql


def test_where():
    sql = mod.Where('foo = ?', 'bar = ?')
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_or():
    sql = mod.Where('foo = ?', 'bar = ?', use_or=True)
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_and_method():
    sql = mod.Where('foo = ?')
    sql.and_('bar = ?')
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_and_operator():
    sql = mod.Where('foo = ?')
    sql &= 'bar = ?'
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_and_with_first_condition():
    sql = mod.Where()
    sql &= 'foo = ?'
    assert str(sql) == 'WHERE foo = ?'


def test_where_with_empty_str():
    sql = mod.Where('')
    assert str(sql) == ''


def test_and_alias():
    sql = mod.Where('foo = ?')
    sql += 'bar = ?'
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_or_method():
    sql = mod.Where('foo = ?')
    sql.or_('bar = ?')
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_or_operator():
    sql = mod.Where('foo = ?')
    sql |= 'bar = ?'
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_or_with_first_condition():
    sql = mod.Where()
    sql |= 'foo = ?'
    assert str(sql) == 'WHERE foo = ?'


def test_empty_where():
    sql = mod.Where()
    assert str(sql) == ''


def test_where_bool():
    sql = mod.Where()
    assert not sql
    sql = mod.Where('foo = ?')
    assert sql


def test_group_by():
    sql = mod.Group('foo')
    assert str(sql) == 'GROUP BY foo'


def test_group_by_multi():
    sql = mod.Group('foo', 'bar')
    assert str(sql) == 'GROUP BY foo, bar'


def test_group_by_having():
    sql = mod.Group('foo', having='bar > 12')
    assert str(sql) == 'GROUP BY foo HAVING bar > 12'


def test_group_by_empty():
    sql = mod.Group()
    assert str(sql) == ''


def test_group_by_bool():
    sql = mod.Group()
    assert not sql
    sql = mod.Group('foo')
    assert sql


def test_order():
    sql = mod.Order('foo')
    assert str(sql) == 'ORDER BY foo ASC'


def test_order_asc_alias():
    sql = mod.Order('+foo')
    assert str(sql) == 'ORDER BY foo ASC'


def test_order_desc():
    sql = mod.Order('-foo')
    assert str(sql) == 'ORDER BY foo DESC'


def test_order_multi():
    sql = mod.Order('foo', '-bar')
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_add_asc():
    sql = mod.Order('foo')
    sql.asc('bar')
    assert str(sql) == 'ORDER BY foo ASC, bar ASC'


def test_order_add_desc():
    sql = mod.Order('foo')
    sql.desc('bar')
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_asc_operator():
    sql = mod.Order('foo')
    sql += 'bar'
    assert str(sql) == 'ORDER BY foo ASC, bar ASC'


def test_order_desc_operator():
    sql = mod.Order('foo')
    sql -= 'bar'
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_empty():
    sql = mod.Order()
    assert str(sql) == ''


def test_order_bool():
    sql = mod.Order()
    assert not sql
    sql = mod.Order('foo')
    assert sql


def test_limit():
    sql = mod.Limit(1)
    assert str(sql) == 'LIMIT 1'


def test_limit_offset():
    sql = mod.Limit(1, 2)
    assert str(sql) == 'LIMIT 1 OFFSET 2'


def test_offset_only():
    sql = mod.Limit(offset=2)
    assert str(sql) == ''


def test_empty_limit():
    sql = mod.Limit()
    assert str(sql) == ''


def test_limit_bool():
    sql = mod.Limit()
    assert not sql
    sql = mod.Limit(1)
    assert sql
    sql = mod.Limit(offset=2)
    assert not sql


def test_select():
    sql = mod.Select()
    assert str(sql) == 'SELECT *;'


def test_select_what_iter():
    sql = mod.Select(['foo', 'bar'])
    assert str(sql) == 'SELECT foo, bar;'


def test_select_from():
    sql = mod.Select('*', 'foo')
    assert str(sql) == 'SELECT * FROM foo;'


def test_select_from_multiple():
    sql = mod.Select('*', ['foo', 'bar'])
    assert str(sql) == 'SELECT * FROM foo , bar;'


def test_select_from_with_cls():
    sql = mod.Select('*', mod.From('foo', 'bar', join='CROSS'))
    assert str(sql) == 'SELECT * FROM foo CROSS JOIN bar;'


def test_select_tables_attrib():
    sql = mod.Select(sets='foo')
    sql.sets.join('bar', mod.From.CROSS)
    assert str(sql) == 'SELECT * FROM foo CROSS JOIN bar;'


def test_select_where():
    sql = mod.Select('*', where='a = b')
    assert str(sql) == 'SELECT * WHERE a = b;'


def test_select_where_multiple():
    sql = mod.Select('*', where=['a = b', 'c = d'])
    assert str(sql) == 'SELECT * WHERE a = b AND c = d;'


def test_select_where_cls():
    sql = mod.Select('*', where=mod.Where('a = b', 'c = d', use_or=True))
    assert str(sql) == 'SELECT * WHERE a = b OR c = d;'


def test_select_where_attrib():
    sql = mod.Select(where='a = b')
    sql.where |= 'c = d'
    assert str(sql) == 'SELECT * WHERE a = b OR c = d;'


def test_select_group_by():
    sql = mod.Select('COUNT(*) AS count', group='foo')
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo;'


def test_select_group_by_multiple():
    sql = mod.Select('COUNT(*) AS count', group=['foo', 'bar'])
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo, bar;'


def test_select_group_by_cls():
    sql = mod.Select('COUNT(*) AS count', group=mod.Group('foo'))
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo;'


def test_select_group_attr():
    sql = mod.Select('COUNT(*) AS count', group='foo')
    sql.group.having = 'bar > 12'
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo HAVING bar > 12;'


def test_select_order():
    sql = mod.Select(order='foo')
    assert str(sql) == 'SELECT * ORDER BY foo ASC;'


def test_select_order_multiple():
    sql = mod.Select(order=['foo', '-bar'])
    assert str(sql) == 'SELECT * ORDER BY foo ASC, bar DESC;'


def test_select_order_cls():
    sql = mod.Select(order=mod.Order('foo'))
    assert str(sql) == 'SELECT * ORDER BY foo ASC;'


def test_select_order_attr():
    sql = mod.Select(order='foo')
    sql.order.desc('bar')
    assert str(sql) == 'SELECT * ORDER BY foo ASC, bar DESC;'


def test_select_limit():
    sql = mod.Select(limit=1)
    assert str(sql) == 'SELECT * LIMIT 1;'


def test_select_limit_offset():
    sql = mod.Select(limit=1, offset=20)
    assert str(sql) == 'SELECT * LIMIT 1 OFFSET 20;'


def test_select_offset_without_limit():
    sql = mod.Select(offset=20)
    assert str(sql) == 'SELECT *;'


def test_select_limit_attr():
    sql = mod.Select()
    sql.limit = 1
    assert str(sql) == 'SELECT * LIMIT 1;'


def test_select_offset_attr():
    sql = mod.Select(limit=1)
    sql.offset = 20
    assert str(sql) == 'SELECT * LIMIT 1 OFFSET 20;'


def test_update():
    sql = mod.Update('foo', foo='?', bar='?')
    assert str(sql) == 'UPDATE foo SET foo = ?, bar = ?;'


def test_update_where():
    sql = mod.Update('foo', foo='?', where='bar = ?')
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ?;'


def test_update_where_multi():
    sql = mod.Update('foo', foo='?', where=['bar = ?', 'baz = ?'])
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ? AND baz = ?;'


def test_update_where_attr():
    sql = mod.Update('foo', foo='?', where='bar = ?')
    sql.where += 'baz = ?'
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ? AND baz = ?;'


def test_delete():
    sql = mod.Delete('foo')
    assert str(sql) == 'DELETE FROM foo;'


def test_delete_where():
    sql = mod.Delete('foo', where='foo = ?')
    assert str(sql) == 'DELETE FROM foo WHERE foo = ?;'


def test_delete_where_multi():
    sql = mod.Delete('foo', where=['foo = ?', 'bar = ?'])
    assert str(sql) == 'DELETE FROM foo WHERE foo = ? AND bar = ?;'


def test_delete_where_attrib():
    sql = mod.Delete('foo', where='foo = ?')
    sql.where += 'bar = ?'
    assert str(sql) == 'DELETE FROM foo WHERE foo = ? AND bar = ?;'


def test_delete_empty_where():
    sql = mod.Delete('foo', where='')
    assert str(sql) == 'DELETE FROM foo;'


def test_insert():
    sql = mod.Insert('foo', vals=mod.sqlarray(3))
    assert str(sql) == 'INSERT INTO foo VALUES (?, ?, ?);'


def test_insert_list():
    sql = mod.Insert('foo', vals=[':foo', ':bar', ':baz'])
    assert str(sql) == 'INSERT INTO foo VALUES (:foo, :bar, :baz);'


def test_insert_naked_vals():
    sql = mod.Insert('foo', vals=':foo, :bar, :baz')
    assert str(sql) == 'INSERT INTO foo VALUES (:foo, :bar, :baz);'


def test_insert_with_cols():
    sql = mod.Insert('foo', cols=['foo', 'bar'], vals=':foo, :bar')
    assert str(sql) == 'INSERT INTO foo (foo, bar) VALUES (:foo, :bar);'


def test_inset_without_vals():
    sql = mod.Insert('foo', cols=['foo', 'bar'])
    assert str(sql) == 'INSERT INTO foo (foo, bar) VALUES (:foo, :bar);'


def test_insert_withot_vals_and_cols():
    try:
        mod.Insert('foo')
        assert False, 'Expected to raise'
    except ValueError:
        pass


def test_replace():
    sql = mod.Replace('foo', ':foo, :bar')
    assert str(sql) == 'REPLACE INTO foo VALUES (:foo, :bar);'


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
    assert conn.close == sqlite3.connect().close
    assert conn.cursor == sqlite3.connect().cursor
    assert conn.isolation_level == sqlite3.connect().isolation_level


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


@mock.patch(MOD + '.Database')
def test_database_plugins_connects(Database):
    """ When database name is passed as string, connection is made """
    mod.database_plugin('foo.db')
    Database.connect.assert_called_once_with('foo.db')


@mock.patch(MOD + '.Database')
def test_database_plugin_does_not_connect_if_connection_is_passed(Database):
    """ When connection object is passed, connection is not made """
    mod.database_plugin(mock.Mock())
    assert not Database.connect.called


