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
    assert c.get_export('routes') == ['librarian.routes.auth.LoginForm', 'librarian.routes.files.FileList']


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
    assert list(r.get_ordered_members()) == [bar, baz, foo]


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


def test_registry_with_reverse_ordering():
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
    r.reverse_order = True
    r.register(foo)
    r.register(bar)
    r.register(baz)
    assert list(r.get_ordered_members()) == [baz, bar, foo]


# OBJECT COLLECTION MIXIN


def test_object_collect():
    class MyCollector(mod.ObjectCollectorMixin):
        def __init__(self):
            self.collected = []

        def register(self, obj):
            self.collected.append(obj)
    comp = mock.Mock()
    comp.get_export.return_value = [1, 2, 3]
    comp.get_object.side_effect = ('foo', 'bar', 'baz')
    m = MyCollector()
    m.collect(comp)
    assert m.collected == ['foo', 'bar', 'baz']


def test_object_collect_with_exception():
    class MyCollector(mod.ObjectCollectorMixin):
        def __init__(self):
            self.collected = []

        def register(self, obj):
            self.collected.append(obj)
    comp = mock.Mock()
    comp.get_export.return_value = [1, 2, 3]
    comp.get_object.side_effect = ('foo', ImportError, 'baz')
    m = MyCollector()
    m.collect(comp)
    assert m.collected == ['foo', 'baz']


# REGISTRY INSTALLER MIXIN


@mock.patch.object(mod, 'exts')
def test_registry_installer(exts):
    class MyCollector(mod.RegistryInstallerMixin, mod.ListCollector):
        registry_class = mock.Mock()
        ext_name = 'foo'
    regobj = MyCollector.registry_class.return_value
    supervisor = mock.Mock()
    m = MyCollector(supervisor)
    m.install_member('foo')
    assert exts.foo == regobj
    regobj.register.assert_called_once_with('foo')


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


@mock.patch.object(mod, 'exts')
def test_collector_install_member(exts):
    supervisor = mock.Mock()
    component = mock.Mock()
    component.get_export.return_value = ['foo.bar.baz']
    collector = component.get_object.return_value
    c = mod.Collectors(supervisor)
    c.collect(component)
    c.install()
    exts.exports.add_collector.assert_called_once_with(collector)


# EXPORTS CLASS


@mock.patch.object(mod, 'exts')
def test_get_components(exts):
    exts.config = {'app.components': ['foo', 'bar', 'baz'], 'root_pkg': 'root'}
    e = mod.Exports(mock.Mock())
    assert e.get_components() == ['root', 'foo', 'bar', 'baz']


@mock.patch.object(mod, 'exts')
def test_exports_init_with_default_collectors(exts):
    exts.config = {'app.components': ['foo', 'bar', 'baz'], 'root_pkg': 'root'}
    e = mod.Exports(mock.Mock())
    assert list(e.collectors) == [mod.Collectors]


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod, 'Component')
def test_exports_component_load(Component, exts):
    exts.config = {'app.components': ['foo', 'bar', 'baz'], 'root_pkg': 'root'}
    e = mod.Exports(mock.Mock())
    e.load_components()
    assert len(e.initialized) == 4
    Component.assert_has_calls([
        mock.call('root'),
        mock.call('foo'),
        mock.call('bar'),
        mock.call('baz')
    ])


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod, 'Component')
def test_exports_component_load_fail(Component, exts):
    exts.config = {'app.components': ['foo', 'bar', 'baz'], 'root_pkg': 'root'}
    Component.side_effect = ImportError
    e = mod.Exports(mock.Mock())
    e.load_components()
    assert len(e.initialized) == 0
