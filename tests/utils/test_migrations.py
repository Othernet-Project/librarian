import sys
import tempfile

import mock

from librarian.utils import migrations as mod

MOD = mod.__name__


def mock_module():
    f, path = tempfile.mkstemp()
    with open(path, 'w') as fd:
        fd.write("""
def up(db, conf):
    db.query("SELECT 'foo';")
        """)
    fd = open(path, 'r')
    return fd


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules(listdir):
    """ Can list Python modules from specified directory """
    listdir.return_value = ['01_test.py', '02_test.py']
    m = mod.get_mods('foo')
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_no_dupes(listdir):
    """ Listing modules does not return duplicates """
    listdir.return_value = ['01_test.py', '01_test.pyc', '02_test.py']
    m = mod.get_mods('foo')
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_ignores_non_migration_files(listdir):
    """ Listing modules will not return modules aren't migrations """
    listdir.return_value = ['__init__.py', 'foo.py', '01_test.py',
                            '02_test.py']
    m = mod.get_mods('foo')
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_can_use_any_number_of_digits(listdir):
    """ Migration numbering is not limited by number of digits """
    listdir.return_value = ['00001_test.py', '00002_test.py']
    m = mod.get_mods('foo')
    assert list(m) == ['00001_test', '00002_test']


def test_get_migrations_lists_migrations_to_run():
    """ Given migration version, migratable modules are selected """
    m = mod.get_new(['01_test', '02_test', '03_test'], 2)
    assert list(m) == [('02_test', 2), ('03_test', 3)]


def test_get_migration_list_correct_order():
    """ Even if migrations are not in correct order, they are reordered """
    m = mod.get_new(['03_test', '01_test', '02_test'], 2)
    assert list(m) == [('02_test', 2), ('03_test', 3)]


@mock.patch(MOD + '.imp.find_module', autospec=True)
def test_load_migration(find_module):
    """ Migration module is loaded """
    find_module.side_effect = [
        (mock_module(), '/foo/__init__.py', ('.py', 'U', 1)),
        (mock_module(), '/foo/01_test.py', ('.py', 'U', 1))
    ]
    m = mod.load_mod('01_test', '/foo')
    find_module.assert_has_calls([
        mock.call('__init__', ['/foo']),
        mock.call('01_test', ['/foo']),
    ])
    assert 'db_migrations' in sys.modules
    assert sys.modules['db_migrations.01_test'] == m
    assert hasattr(m, 'up')
    del sys.modules['db_migrations.01_test']  # cleanup
    del sys.modules['db_migrations']  # cleanup


@mock.patch(MOD + '.imp.find_module', autospec=True)
def test_load_migration_twice(find_module):
    """ Migration module is not loaded twice if it's found in sys.modules """
    find_module.return_value = (mock_module(), '/foo/01_test.py',
                                ('.py', 'U', 1))
    mod.load_mod('01_test', '/foo')
    mod.load_mod('01_test', '/foo')
    assert find_module.call_count == 2
    del sys.modules['db_migrations.01_test']  # cleanup
    del sys.modules['db_migrations']  # cleanup


@mock.patch(MOD + '.imp.find_module', autospec=True)
def test_load_migration_custom_prefix(find_module):
    find_module.return_value = (mock_module(), '/foo/01_test.py',
                                ('.py', 'U', 1))
    mod.load_mod('01_test', '/foo', prefix='librarian.migrations')
    assert 'librarian.migrations.01_test' in sys.modules
    del sys.modules['librarian.migrations.01_test']
    del sys.modules['librarian.migrations']  # cleanup


def test_get_migration_version():
    """ Returns migration version based on database table """
    db = mock.Mock()
    ret = mod.get_version(db)
    assert db.query.called
    assert ret == db.result.version


def test_create_table_if_no_version_table():
    """ Version-tracking table is crated if it doesn't exist """
    import sqlite3
    db = mock.Mock()
    db.query.side_effect = [sqlite3.OperationalError('no such table'), None,
                            None]
    try:
        ret = mod.get_version(db)
    except Exception:
        assert False, 'Expected not to raise'
    assert ret == 0
    db.query.assert_any_call(mod.MIGRATION_TABLE_SQL)
    db.query.assert_any_call(mod.REPLACE_SQL, 0)


def test_run_migration():
    """ Running migration calls module's ``up()`` method """
    db = mock.Mock()
    db.transaction.return_value.__enter__ = lambda x: None
    db.transaction.return_value.__exit__ = lambda x, y, z, n: None
    m = mock.Mock()
    mod.run_migration(1, db, m)
    m.up.assert_called_once_with(db, {})
    db.query.assert_called_once_with(mod.REPLACE_SQL, 1)


@mock.patch(MOD + '.logging')
@mock.patch(MOD + '.get_version')
@mock.patch(MOD + '.get_mods')
@mock.patch(MOD + '.get_new')
@mock.patch(MOD + '.load_mod')
@mock.patch(MOD + '.run_migration')
def test_migrate(run, load_mod, get_new, get_mods, get_version, *ignored):
    get_version.return_value = 2
    get_mods.return_value = ['01_test', '02_test', '03_test']
    get_new.return_value = [('03_test', 3)]
    db = mock.Mock()
    mod.migrate(db, '/foo', 'mypkg', {})
    get_version.assert_called_once_with(db)
    get_mods.assert_called_once_with('/foo')
    get_new.assert_called_once_with(get_mods.return_value, 3)
    load_mod.assert_called_once_with('03_test', '/foo', 'mypkg')
    run.assert_called_once_with(3, db, load_mod.return_value, {})
    assert db.refresh_table_stats.called

