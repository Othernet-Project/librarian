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
    mocked_pkg = mock.Mock()
    mocked_pkg.__path__ = ['foo']
    m = mod.get_mods(mocked_pkg)
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_no_dupes(listdir):
    """ Listing modules does not return duplicates """
    listdir.return_value = ['01_test.py', '01_test.pyc', '02_test.py']
    mocked_pkg = mock.Mock()
    mocked_pkg.__path__ = ['foo']
    m = mod.get_mods(mocked_pkg)
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_ignores_non_migration_files(listdir):
    """ Listing modules will not return modules aren't migrations """
    listdir.return_value = ['__init__.py', 'foo.py', '01_test.py',
                            '02_test.py']
    mocked_pkg = mock.Mock()
    mocked_pkg.__path__ = ['foo']
    m = mod.get_mods(mocked_pkg)
    assert sorted(list(m)) == ['01_test', '02_test']


@mock.patch(MOD + '.os.listdir', autospec=True)
def test_list_modules_can_use_any_number_of_digits(listdir):
    """ Migration numbering is not limited by number of digits """
    listdir.return_value = ['00001_test.py', '00002_test.py']
    mocked_pkg = mock.Mock()
    mocked_pkg.__path__ = ['foo']
    m = mod.get_mods(mocked_pkg)
    assert list(m) == ['00001_test', '00002_test']


def test_get_migrations_lists_migrations_to_run():
    """ Given migration version, migratable modules are selected """
    m = mod.get_new(['01_test', '02_test', '03_test'], 2)
    assert list(m) == [('02_test', 2), ('03_test', 3)]


def test_get_migration_list_correct_order():
    """ Even if migrations are not in correct order, they are reordered """
    m = mod.get_new(['03_test', '01_test', '02_test'], 2)
    assert list(m) == [('02_test', 2), ('03_test', 3)]


@mock.patch.object(mod.importlib, 'import_module')
def test_load_migration(import_module):
    mocked_pkg = mock.Mock()
    mocked_pkg.__name__ = 'mypkg'
    mocked_mod = mock_module()
    import_module.return_value = mocked_mod
    assert mod.load_mod('01_test', mocked_pkg) is mocked_mod
    import_module.assert_called_once_with('mypkg.01_test', package='mypkg')


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
@mock.patch.object(mod.importlib, 'import_module')
def test_migrate(import_module, run, load_mod, get_new, get_mods, get_version,
                 *ignored):
    mocked_pkg = mock.MagicMock()
    mocked_pkg.__package__ = 'mypkg'
    import_module.return_value = mocked_pkg
    get_version.return_value = 2
    get_mods.return_value = ['01_test', '02_test', '03_test']
    get_new.return_value = [('03_test', 3)]
    db = mock.Mock()
    mod.migrate(db, 'mypkg', {})
    import_module.assert_called_once_with('mypkg')
    get_version.assert_called_once_with(db)
    get_mods.assert_called_once_with(mocked_pkg)
    get_new.assert_called_once_with(get_mods.return_value, 3)
    load_mod.assert_called_once_with('03_test', mocked_pkg)
    run.assert_called_once_with(3, db, load_mod.return_value, {})
    assert db.refresh_table_stats.called
