import os
import pytest

try:
    from unittest import mock
except ImportError:
    import mock


from librarian.core import exports as mod


MOD = mod.__name__
TESTDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PKGDIR = os.path.dirname(TESTDIR)


# DECORATORS


deptests = [
    ('foo.bar', 'foo.bar'),
    (['foo.bar', 'bar.baz'], ['foo.bar', 'bar.baz']),
    (None, None),
    ('', ''),
]


@pytest.mark.parametrize('deps,attr', deptests)
def test_metadata_decorator(deps, attr):
    @mod._metadata(deps, 'foo')
    def foo():
        pass
    assert foo.foo == attr


@pytest.mark.parametrize('deps,attr', deptests)
def test_depends_on_decorator(deps, attr):
    @mod.depends_on(deps)
    def foo():
        pass
    assert foo.depends_on == attr


@pytest.mark.parametrize('deps,attr', deptests)
def test_required_by_decorator(deps, attr):
    @mod.required_by(deps)
    def foo():
        pass
    assert foo.required_by == attr


def test_combined():
    @mod.depends_on('foo')
    @mod.required_by('bar')
    def foo():
        pass
    assert foo.depends_on == 'foo'
    assert foo.required_by == 'bar'


# BASE FUNCTIONALITY


def test_doubledot_patterns():
    leading = mod.DOUBLEDOT[0][0]
    assert leading.search('../foo/')
    assert not leading.search('/foo/')
    assert leading.sub('', '../foo/') == 'foo/'

    middle = mod.DOUBLEDOT[1][0]
    assert middle.search('/foo/../bar/')
    assert not middle.search('/foo/..bar/')
    assert middle.sub('/', '/foo/../bar/') == '/foo/bar/'
    assert middle.sub('/', '/foo/../../bar/') == '/foo/bar/'

    trailing = mod.DOUBLEDOT[2][0]
    assert trailing.search('/foo/..')
    assert not trailing.search('/foo/')
    assert trailing.sub('', '/foo/..') == '/foo'


@pytest.mark.parametrize('path,out', [
    ('foo/bar/baz/', 'foo/bar/baz'),
    ('/foo/bar/baz', 'foo/bar/baz'),
    ('foo/bar../baz', 'foo/bar../baz'),
    ('foo/bar..baz/', 'foo/bar..baz'),
    ('../foo/bar', 'foo/bar'),
    ('foo/bar/../../..', 'foo/bar'),
    ('foo/../../../bar', 'foo/bar'),
])
def test_strip_paths(path, out):
    assert mod.strip_path(path) == out


@pytest.mark.parametrize('name,out', [
    ('foo.bar', 'librarian.core.foo.bar'),
    ('.foo.bar', 'librarian.core.foo.bar'),
    ('foo..bar', 'librarian.core.foo.bar'),
    ('foo...bar', 'librarian.core.foo.bar'),
    ('..foo.bar', 'librarian.core.foo.bar'),
    ('foo.bar..', 'librarian.core.foo.bar'),
])
def test_fully_qualified_name(name, out):
    from librarian import core
    assert mod.fully_qualified_name(core, name) == out


# COMPONENT


def test_component_init():
    import librarian
    c = mod.Component('librarian')
    assert c.pkg == librarian
    # FIXME: Is there a better way to get this path?
    libpath = os.path.abspath(os.path.dirname(librarian.__file__))
    assert c.pkgdir == libpath


def test_component_init_import_error():
    with pytest.raises(ImportError):
        mod.Component('bogus')


@pytest.mark.parametrize('path', [
    'core',
    'core/exports.py',
    'config.ini',
])
def test_component_path(path):
    c = mod.Component('librarian')
    assert c.pkgpath(path)


def test_component_missing_path():
    c = mod.Component('librarian')
    with pytest.raises(ValueError):
        c.pkgpath('bogus')


def test_config_path():
    import librarian
    c = mod.Component('librarian')
    # FIXME: Is there a better way to get this path?
    libpath = os.path.abspath(os.path.dirname(librarian.__file__))
    assert c.config_path == os.path.join(libpath, 'config.ini')


@mock.patch.object(mod.Component, 'config_path',
                   new_callable=mock.PropertyMock)
def test_config_parsing(config_path):
    config_path.return_value = os.path.join(TESTDIR, 'samples/config.ini')
    c = mod.Component('librarian')
    assert c.config['app.foo'] == 'bar'


@mock.patch.object(mod.Component, 'config_path',
                   new_callable=mock.PropertyMock)
def test_config_exports(config_path):
    config_path.return_value = os.path.join(TESTDIR, 'samples/config.ini')
    c = mod.Component('librarian')
    assert c.get_export('databases') == ['facets', 'files', 'notifications']


# BASE COLLECTOR CLASSES


def test_registry():
    @mod.depends_on('bar')  # must come after bar
    def foo():
        pass
    foo.name = 'foo'

    def bar():
        pass
    bar.name = 'bar'

    @mod.required_by('foo')  # must come before foo
    def baz():
        pass
    baz.name = 'baz'

    r = mod.DependencyCollector(mock.Mock())
    r.register(foo)
    r.register(bar)
    r.register(baz)
    assert list(r.get_ordered_members()) == [baz, bar, foo]


def test_missing_dependency():
    @mod.depends_on('bar')  # must come after bar
    def foo():
        pass
    foo.name = 'foo'

    @mod.required_by('baz')  # must come before foo
    def bar():
        pass
    bar.name = 'bar'

    r = mod.DependencyCollector(mock.Mock())
    r.register(foo)
    r.register(bar)
    with pytest.raises(r.UnresolvableDependency):
        list(r.get_ordered_members())


def test_registry_with_no_dependencies():
    def foo():
        pass
    foo.name = 'foo'

    def bar():
        pass
    bar.name = 'bar'

    def baz():
        pass
    baz.name = 'baz'

    r = mod.DependencyCollector(mock.Mock())
    r.register(foo)
    r.register(bar)
    r.register(baz)
    assert list(r.get_ordered_members()) == [foo, bar, baz]


# COLLECTORS COLLECTOR


def test_collector_collection():
    supervisor = mock.Mock()
    component = mock.Mock()
    component.get_export.return_value = ['foo.bar.baz']
    collector = component.get_object.return_value
    c = mod.Collectors(supervisor)
    c.collect(component)
    assert c.registry == [collector]


def test_collector_importerror():
    supervisor = mock.Mock()
    component = mock.Mock()
    component.get_export.return_value = ['foo.bar.baz']
    component.get_object.side_effect = ImportError
    c = mod.Collectors(supervisor)
    c.collect(component)  # <-- no exception
    assert c.registry == []


def test_collector_with_invalid_methods():
    supervisor = mock.Mock()
    component = mock.Mock()
    component.get_export.return_value = ['foo.bar.baz']
    collector = component.get_object.return_value
    del collector.install
    c = mod.Collectors(supervisor)
    c.collect(component)
    assert c.registry == []


def test_collector_install_member():
    supervisor = mock.Mock()
    component = mock.Mock()
    component.get_export.return_value = ['foo.bar.baz']
    collector = component.get_object.return_value
    c = mod.Collectors(supervisor)
    c.collect(component)
    c.install()
    supervisor.exports.add_collector.assert_called_once_with(collector)


# EXPORTS CLASS


def test_get_components():
    supervisor = mock.Mock()
    supervisor.ROOT_PKG = 'root'
    supervisor.config = {'app.components': ['foo', 'bar', 'baz']}
    e = mod.Exports(supervisor)
    assert e.get_components() == ['root', 'foo', 'bar', 'baz']


def test_exports_init_with_default_collectors():
    supervisor = mock.Mock()
    supervisor.ROOT_PKG = 'root'
    supervisor.config = {'app.components': ['foo', 'bar', 'baz']}
    e = mod.Exports(supervisor)
    assert list(e.collectors) == [mod.Collectors]


def test_exports_init_adds_supervisor_exports_attr():
    supervisor = mock.Mock()
    supervisor.ROOT_PKG = 'root'
    supervisor.config = {'app.components': ['foo', 'bar', 'baz']}
    e = mod.Exports(supervisor)
    assert supervisor.exports is e


@mock.patch(MOD + '.Component')
def test_exports_component_load(Component):
    supervisor = mock.Mock()
    supervisor.ROOT_PKG = 'root'
    supervisor.config = {'app.components': ['foo', 'bar', 'baz']}
    e = mod.Exports(supervisor)
    e.load_components()
    assert len(e.initialized) == 4
    Component.assert_has_calls([
        mock.call('root'),
        mock.call('foo'),
        mock.call('bar'),
        mock.call('baz')
    ])


@mock.patch(MOD + '.Component')
def test_exports_component_load_fail(Component):
    supervisor = mock.Mock()
    supervisor.ROOT_PKG = 'root'
    supervisor.config = {'app.components': ['foo', 'bar', 'baz']}
    Component.side_effect = ImportError
    e = mod.Exports(supervisor)
    e.load_components()
    assert len(e.initialized) == 0
