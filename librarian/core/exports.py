"""
This module contains the functions and classes for working with component
exports.
"""

# Copyright 2016, Outernet Inc.
# Some rights reserved.
#
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.

import os
import logging
import functools
from os.path import join

from confloader import ConfDict
from disentangler import Disentangler

from .exceptions import EarlyExit
from .utils.collectors import (
    muter,
    to_list,
    hasmethod,
    strip_path,
    import_package,
    import_object,
    fully_qualified_name,
)
from .exts import ext_container as exts

try:
    unicode = unicode
except NameError:
    unicode = str


# EVENT NAMES

#: Event name used to signal that a member group has been collected
MEMBER_GROUP_COLLECTED = 'exp.collected'

#: Event name used to signal that a member group has finished installing
MEMBER_GROUP_INSTALLED = 'exp.installed'

#: Event named used to signal the end of exports processing
EXPORTS_FINISHED = 'exp.finished'


# DECORATORS

def _metadata(data, name):
    """
    Generic decorator that adds metadata in list form to the decorated
    function. The ``data`` attribute is a string or a list of strings. If the
    value is a single string, it will be convereted to a list.
    """
    def decorator(fn):
        setattr(fn, name, data)
        return fn
    return decorator

#: Decorator that marks the dependencies for a given function. The ``deps``
#: argument should be a string or a list of strings, where each string
#: identifies the dependency. The identifier is specific to the type of
#: object.
#:
#: The dependency list is turned into an attribute on the function object.
depends_on = functools.partial(_metadata, name='depends_on')
after = depends_on

#: Decorator that marks the dependents of a given function. The ``deps``
#: argument should be a string or a list of strings, where each string
#: identifies the dependency. The identifier is specific to the type of
#: object.
#:
#: The dependents list is turned into an attribute on the function object.
required_by = functools.partial(_metadata, name='required_by')
before = depends_on

#: Decorator that marks a function that is executed for a certain vent.
hook = functools.partial(_metadata, name='hook')


def command(name, flags, extra_arguments=[], **kwargs):
    """
    Decorator that marks a function as a command handler.

    The ``name`` argument will be used to identify the argument that will
    trigger this command (and is also used as ``dest`` argument to the
    ``argparse.ArgumentParser.add_argument()`` method.

    The ``flags`` argument is either the argument name or command line flags.

    Any additional keyword arguments will be passed to the parser's
    ``add_argument()`` method.

    If the handler needs to register additional arguments, they may be passed
    as an iterable of dicts using the optional ``extra_arguments`` argument.
    The dicts will be passed to the parser's ``add_argument()`` as kwargs.
    """
    def decorator(fn):
        fn.name = name
        fn.flags = flags
        fn.kwargs = kwargs
        fn.extra_arguments = extra_arguments
        return fn
    return decorator


def get_object_name(obj):
    """
    Return object's name. If object has a :py:attr:`name` attribute, it will be
    used. Otherwise a combination of object's module and Python name are used
    (e.g., if object 'foo' is found in 'bar.baz' module, then the name would be
    'baz.bar.foo').
    """
    return getattr(obj, 'name', None) or '{}.{}'.format(obj.__module__,
                                                        obj.__name__)


class ComponentError(Exception):
    """
    Error raised when there is an issue with a component. The component object
    is accessible through the :py:attr:`~ComponentError.component`
    attribute.
    """
    def __init__(self, msg, component):
        self.component = component
        super(ComponentError, self).__init__(msg)

    def __str__(self):
        return 'Error in {}: {}'.format(self.component, self.args[0])


class Component(object):
    """
    This class encapsulates a single component. It is instantiated with a fully
    qualified name of the package, and provides methods for accessing modules
    and files within the package directory.

    During initialization, the instance will try to import the package. Import
    errors during the load are not trapped.
    """

    #: Default configuration path
    CONFIG_PATH = 'config.ini'

    def __init__(self, name):
        self.name = name
        self.pkg, self.pkgdir = import_package(name)
        self._config_path = getattr(self.pkg, 'CONFIG', self.CONFIG_PATH)
        self._config = None

    def pkgpath(self, relpath, noerror=False):
        """
        Return the absolute path of a file or directory located at ``relpath``
        within the package. If the path is not found, :py:exc:`ValueError` is
        raised. The ``noerror`` argument can be used to suppress the exception
        and return ``None``.
        """
        path = join(self.pkgdir, strip_path(relpath))
        if not os.path.exists(path):
            if noerror:
                return
            raise ValueError('No file or folder at {}'.format(path))
        return path

    def fully_qualified_name(self, name):
        """
        Return a fully qualified name of an object whose name is specified as
        relative name in dotted notation.
        """
        return fully_qualified_name(self.pkg, name)

    def get_object(self, name):
        """
        Import and return an object that matches a name specified as relative
        name in dotted notation.
        """
        return import_object(self.fully_qualified_name(name))

    @property
    def config_path(self):
        """
        Path of the configuration file.
        """
        return self.pkgpath(self._config_path)

    @property
    def config(self):
        """
        Return component configuration. The configuration is parsed using
        confloader and return as a :py:class:`~confloader.ConfDict` instance.
        The parsed configuration is cached so accessing this property multiple
        times has no parsing overhead after the first time.
        """
        if not self._config:
            self._config = ConfDict.from_file(self.config_path)
        return self._config

    def get_export(self, key, default=None):
        """
        Shortcut for accessing 'exports.'-prefixed key form the configuration.

        The value of the ``default`` argument is returned if the key is not
        found in the configuration or if the configuration file is missing.
        """
        try:
            return self.config.get('{}.{}'.format('exports', key), default)
        except ValueError:
            return default


class Collector(object):
    """
    This is the base class for member group collectors. This class defines two
    stub methods that must be implemented in all subclasses.

    All member group classes are instantiated with a supervisor instance. The
    supervisor instance is available through the :py:attr:`supervisor`
    attribute. Additionally, the events extension is available as
    :py:attr:`events` attribute.

    The subclasses should be based on one of the more concrete
    :py:class:`ListCollector` and :py:class:`DepenencyCollector` classes,
    though this class is a perfectly valid base for collectors.
    """
    #: Whether component order should be reversed before installation
    reverse_order = False

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.events = exts.events

    @property
    def type(self):
        """
        Returns a string that identifies the member group.
        """
        return self.__class__.__name__.lower()

    def collect(self, component):
        """
        This method must be implemneted by a subclass. The caller must invoke
        the method with a :py:class:`Component` instance.  This method must
        call the :py:meth:`register` method to register collected objects.
        """
        raise NotImplementedError('Subclass must implement this method')

    def collectall(self, components):
        """
        Collect all components from the given list. The ``components`` argument
        should be an iterable of :py:class:`Component` objects. The
        :py:meth:`~Collector.collect` method is called on each object in the
        iterable. Exceptions in the :py:meth:`~Collector.collect` method are
        silenced and logged.

        When collection is finished, a :py:data:`MEMBER_GROUP_COLLECTED` event
        is fired.
        """
        for component in components:
            try:
                self.collect(component)
            except Exception:
                logging.exception('{} failed to collect {}'.format(
                    self.type, component.name))
        self.events.publish(MEMBER_GROUP_COLLECTED, group_type=self.type)

    def get_ordered_members(self):
        """
        This method must be overloaded in the subclass to return a correctly
        ordered list of members to install.
        """
        raise NotImplementedError('Subclass must implement this method')

    def install_member(self, member):
        """
        This method must be overloaded in the subclass to install a component
        member. The method is invoked with a single component member.
        """
        raise NotImplementedError('Subclass must implement this method')

    def pre_install(self):
        """
        Method called before installation starts.
        """
        pass

    def post_install(self):
        """
        Method called after installation is done.
        """
        pass

    def install(self):
        """
        Install all component members from this group. After installing is
        finished, a :py:data:`MEMBER_GROUP_INSTALLED` event is fired.
        """
        self.pre_install()
        for member in self.get_ordered_members():
            try:
                self.install_member(member)
            except EarlyExit:
                raise
            except Exception:
                logging.exception(
                    'Error while installing {} member: {}'.format(
                        self.type, member))
        self.post_install()
        self.events.publish(MEMBER_GROUP_INSTALLED, group_type=self.type)


class ObjectCollectorMixin(object):
    """
    Mixin for collectors that collect and register Python objects.
    """
    export_key = None

    def collect(self, component):
        member_list = to_list(component.get_export(self.export_key, []))
        for name in member_list:
            try:
                obj = component.get_object(name)
            except ImportError:
                logging.exception(
                    'Could not import member {} from {}'.format(
                        name, component.name))
                continue
            else:
                self.register(obj)


class RegistryInstallerMixin(object):
    """
    Mixin for collectors that use a registry object to install members. The
    registry class is assumed to be instantiated without any arguments, and is
    stored on exts container under an attribute given by
    :py:attr:`~RegistryInstallerMixin.ext_name`  attribute. The class is
    specified using :py:attr:`~RegistryInstallerMixin.registry_class`
    attribute.

    The registry class must implement a :py:meth:`register` method that takes
    the collected member as its sole argument.
    """
    registry_class = None
    ext_name = None

    def __init__(self, *args, **kwargs):
        super(RegistryInstallerMixin, self).__init__(*args, **kwargs)
        self.regobj = self.registry_class()
        setattr(exts, self.ext_name, self.regobj)

    def install_member(self, member):
        self.regobj.register(member)


class ListCollector(Collector):
    """
    Base collector that provides interfaces for component member registration
    without dependency resolution.
    """

    def __init__(self, supervisor):
        super(ListCollector, self).__init__(supervisor)
        self.registry = []

    def register(self, obj):
        """
        Register an object. This method simply appends the new object to the
        list of registered objects.
        """
        self.registry.append(obj)

    def get_ordered_members(self):
        """
        Generator that yields objects in the order they were registered in.
        """
        ordered = self.registry
        if self.reverse_order:
            ordered = reversed(ordered)
        for obj in ordered:
            yield obj


class DependencyCollector(Collector):
    """
    Base collector that provides intrerfaces for component member registration
    with dependency resolution.
    """

    #: Exception raised when dependency is not resolvable.
    UnresolvableDependency = Disentangler.UnresolvableDependency

    def __init__(self, supervisor):
        super(DependencyCollector, self).__init__(supervisor)
        self.registry = {}
        self.resolver = Disentangler.new()

    def register(self, obj):
        """
        Register an object. Objects are identified by name. This method will
        attempt to get the name of the object using the
        :py:func:`get_object_name` function.

        Objects may have :py:attr:`dependencies` or :py:attr:`dependents`
        attributes which match one of more names of other objects. These
        attributes are used in dependency resolution such that:

        - objects that depend on other objects are always installed after the
          objects they depend on
        - objects that are dependents of other objects are always installed
          _after_ the objects on which they depend
        """
        name = get_object_name(obj)
        self.registry[name] = obj
        dependencies = getattr(obj, 'depends_on', [])
        dependents = getattr(obj, 'required_by', [])
        self.resolver.add(name, {
            'depends_on': to_list(dependencies),
            'required_by': to_list(dependents),
        })

    def get_ordered_members(self):
        """
        Generator that yields members in correct order, taking into account any
        dependencies.
        """
        ordered = self.resolver.solve()
        if self.reverse_order:
            ordered = reversed(ordered)
        for name in ordered:
            yield self.registry[name]


class Collectors(ListCollector):
    """
    This class handles member group collector exports. The member group
    collectors should be :py:class:`Collector` subclasses that manage
    individual groups.
    """
    def collect(self, component):
        collectors = component.get_export('collectors', [])
        for collector in collectors:
            try:
                collector = component.get_object(collector)
            except ImportError:
                logging.exception('Could not import collector: %s', collector)
                continue
            hasmeth = functools.partial(hasmethod, collector)
            if not all([hasmeth('install'), hasmeth('collectall')]):
                logging.error('Invalid API for collector {}'.format(collector))
                continue
            self.register(collector)

    def install_member(self, collector):
        exts.exports.add_collector(collector)


class Exports(object):
    """
    This class manages the exports collection process. It also provides an API
    for extending the collector list with arbitrary user-specified component
    member group collectors.
    """
    #: List of default collectors
    DEFAULT_COLLECTORS = [Collectors]

    #: Name of the configuration key that has the components list
    COMPONENTS_CONF = 'app.components'

    def __init__(self, supervisor):
        self.member_groups = []
        self.supervisor = supervisor
        self.components = self.get_components()
        self.initialized = []
        self.collectors = muter(self.DEFAULT_COLLECTORS)

    def load_components(self):
        """
        Instantiate :py:class:`Component` object for each component in the
        :py:attr:`components` list. Components that cannot be loaded are logged
        and silently dropped. This method can only be invoked once. On
        subsequent calls, it does not do anything.
        """
        if self.initialized:
            return
        for c in self.components:
            try:
                self.initialized.append(Component(c))
            except ImportError:
                logging.exception('Could not load component {}'.format(c))
                continue

    def get_components(self):
        """
        Return a list of components that should participate in the collection
        process. The components are obtained from the key defined by the
        :py:attr:`~Exports.COMPONENTS_CONF` attribute.

        The component that owns the supervisor is always prepended to the list.
        This component is obtained by accessing supervisor's
        :py:attr:`ROOT_PKG` attribute.
        """
        # When getting the component list, we make a copy, so we don't mutate
        # the original found in the configuration.
        comps = exts.config.get(self.COMPONENTS_CONF, [])[:]
        # Add the package in which supervisor is found as first component
        comps.insert(0, exts.config['root_pkg'])
        return comps

    def add_collector(self, collector):
        """
        Add a collector class to the list of collectors.
        """
        self.collectors.append(collector)

    def process_components(self):
        """
        Collect and install all component exports. The
        :py:data:`EXPORTS_FINISHED` event is fired when all components have
        been processed.
        """
        self.collectors.reset()
        for collector_cls in self.collectors:
            collector = collector_cls(self.supervisor)
            # It is assumed here that any exceptions will not bubble up to this
            # level. If an exception somehow manages to bubble up here, there's
            # something wrong with the Collector implementation.
            collector.collectall(self.initialized)
            collector.install()
        exts.events.publish(EXPORTS_FINISHED)
