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
import re
import sys
import logging
import argparse
import functools
import importlib
from os.path import join

from confloader import ConfDict
from disentangler import Disentangler
from squery_pg.squery_pg import DatabaseContainer, Database, migrate


try:
    unicode = unicode
except NameError:
    unicode = str


# EVENT NAMES


#: Event name used to signal that a member group has finished installing
MEMBER_GROUP_INSTALLED = 'exp.installed'

#: Event name used to signal that a database is ready
DATABASE_READY = 'exp.dbready'


# OTHER CONSTANTS


# Replacement patterns for path cleanup
DOUBLEDOT = (
    # Please keep the order intact, it *is* significant!
    (re.compile(r'^\.\./'), ''),
    (re.compile(r'/\.\./(\.\./)*'), '/'),
    (re.compile(r'/\.\.$'), ''),
)

# Replacement pattern for Python name cleanup
MULTIDOTS = re.compile(r'\.\.+')


def to_list(val):
    """
    Make sure strings are lists containing the string.
    """
    if val is None:
        return []
    if type(val) in [bytes, unicode]:
        return [val]
    return val


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


def command(name, flags, extra_arguments=[], *args, **kwargs):
    """
    Decorator that marks a function as a command handler.

    The ``name`` argument will be used to identify the argument that will
    trigger this command (and is also used as ``dest`` argument to the
    ``argparse.ArgumentParser.add_argument()`` method.

    The ``flags`` argument is either the argument name or command line flags.

    Any additional args and kwargs will be passed to the parser's
    ``add_argument()`` method.

    If the handler needs to register additional arguments, they may be passed
    as an iterable of dicts using the optional ``extra_arguments`` argument.
    The dicts will be passed to the parser's ``add_argument()`` as kwargs.
    """
    def decorator(fn):
        fn.name = name
        fn.flags = flags
        fn.args = args
        fn.kwargs = kwargs
        fn.extra_arguments = extra_arguments
        return fn
    return decorator


def import_package(name):
    """
    Import a package give fully qualified name and return the package object as
    well as the absolute path to the package's directory.
    """
    pkg = importlib.import_module(name)
    pkgdir = os.path.dirname(os.path.abspath(pkg.__file__))
    if pkgdir not in sys.path:
        sys.path.append(pkgdir)
    return pkg, pkgdir


def import_object(name):
    """
    Import an object given fully qualified name.

    For a name 'foo.bar.baz', this is equivalent to::

        from foo.bar import baz

    """
    try:
        mod, obj = name.rsplit('.', 1)
    except ValueError:
        raise ImportError('Cannot import name {}'.format(name))
    mod = importlib.import_module(mod)
    try:
        return getattr(mod, obj)
    except AttributeError:
        raise ImportError('Cannot import name {}'.format(name))


def fully_qualified_name(pkg, name):
    """
    Returns fully qualified name of an object given a package object and
    relative name in dotted path notation.

    Example::

        >>> import foo.bar
        >>> MemberGroupBase.fully_qualified_name(foo.bar, 'baz')
        'foo.bar.baz'

    """
    name = MULTIDOTS.sub('.', name)
    name = name.strip('.')
    return '{}.{}'.format(pkg.__name__, name)


def strip_path(path):
    """
    Removes any leading slashes and double-dots from paths and normalizes them.
    """
    path = path.strip()
    for rxp, repl in DOUBLEDOT:
        path = rxp.sub(repl, path)
    return os.path.normpath(path.strip('/'))


def get_object_name(obj):
    """
    Return object's name. If object has a :py:attr:`name` attribute, it will be
    used. Otherwise a combination of object's module and Python name are used
    (e.g., if object 'foo' is found in 'bar.baz' module, then the name would be
    'baz.bar.foo').
    """
    if hasattr(obj, 'name'):
        return obj.name
    else:
        return '{}.{}'.format(obj.__module__, obj.__name__)


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
        return 'Error in {}: {}'.format(self.component, self.msg)


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
        self.config_path = getattr(self.pkg, 'CONFIG', self.CONFIG_PATH)
        self._config = None

    def pkgpath(self, relpath):
        """
        Return the absolute path of a file or directory located at ``relpath``
        within the package. If the path is not found, :py:exc:`ValueError` is
        raised.
        """
        path = join(self.pkgdir, strip_path(relpath))
        if not os.path.exists(path):
            raise ValueError('No file or folder at {}'.format(path))
        return path

    def fully_qualified_name(self, name):
        """
        Return a fully qualified name of an object whose name is specified as
        relative name in dotted notation.
        """
        return fully_qualified_name(self.name, name)

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
        return self.pkgpath(self.config_path)

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


class MemberGroupBase(object):
    """
    This class defines two stub methods that must be implemented in all
    subclasses.

    All member group classes are instantiated with a supervisor instance. The
    supervisor instance is available through the :py:attr:`supervisor`
    attribute. Additionally, the events extension is available as
    :py:attr:`events` attribute.
    """
    #: String that identifies the member group.
    type = None

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.events = self.supervisor.ext.events

    def collect(self, component):
        """
        This method must be implemneted by a subclass. The caller must invoke
        the method with a :py:class:`Component` instance.  This method must
        call the :py:meth:`register` method to register collected objects.
        """
        raise NotImplementedError('Subclass must implement this method')

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
        Called by the supervior to install all component members from this
        group. After installing is finished, a
        :py:data:`MEMBER_GROUP_INSTALLED` event is fired.
        """
        self.pre_install()
        for member in self.get_ordered_members():
            try:
                self.install_member(member)
            except Exception:
                logging.exception(
                    'Error while installing {} member: {}'.format(
                        self.type, member))
        self.events.publish(MEMBER_GROUP_INSTALLED, group_type=self.type)
        self.post_install()


class MemberList(MemberGroupBase):
    """
    Base member list provides interfaces for component member registration
    without dependency resolution. The concrete member lists should implement
    :py:meth:`~Memberlist.install` and :py:meth:`~MemberList.collect methods
    only.
    """

    def __init__(self, supervisor):
        super(MemberList, self).__init__(supervisor)
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
        for obj in self.registry:
            yield obj


class MemberDependencyList(MemberGroupBase):
    """
    Base registry class that provides intrerfaces for component member
    registration and dependency resolution. The concrete member registries
    should implement the :py:meth:`~MemberDependencyList.install` and
    :py:meth:`~MemberDependencyList.collect` methods only.
    """

    #: Exception raised when dependency is not resolvable.
    UnresolvableDependency = Disentangler.UnresolvableDependency

    def __init__(self, supervisor):
        super(MemberDependencyList, self).__init__(supervisor)
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
        for name in ordered:
            yield self.registry[name]


class Configuration(MemberList):
    """
    This class manages component-specific configuration.
    """
    type = 'configuration'

    def collect(self, component):
        self.register(component)

    def install_member(self, component):
        for k, v in component.config.items():
            if k.startswith('exports.'):
                # Omit exports from master configuration
                continue
            self.supervisor.config[k] = v


def Commands(MemberList):
    """
    This class manages command argument handlers.
    """
    type = 'commands'

    def __init__(self, supervisor):
        super(Commands, self).__init__(supervisor)
        self.parser = argparse.ArgumentParser()
        self.handlers = {}

    def collect(self, component):
        commands = component.get_export('commands', [])
        for command in commands:
            try:
                handler = component.get_object(command)
            except ImportError:
                logging.error('Could not load handler {} for component '
                              '{}'.format(command, component.name))
                continue
            if not hasattr(handler, 'name'):
                logging.error('Invalid handler {} for component {}'.format(
                    command, component.name))
                continue
            handler.component = component.name
            self.register(handler)

    def install_member(self, handler):
        name = handler.name
        if name in self.handlers:
            logging.warn('Duplicate registration for command: {}'.format(name))
            return
        self.handlers[name] = handler
        kwargs = handler.kwargs.copy()
        kwargs['dest'] = name
        args = to_list(handler.flags)
        args.extend(list(handler.args))
        self.parser.add_argument(*args, **kwargs),
        for arg in handler.extra_args:
            self.parser.add_argument(**arg)

    def post_install(self):
        args = self.parser.parse_args()
        arglist = list(vars(args).keys())
        for name, handler in self.handlers:
            if name in arglist:
                handler(args)


class Databases(MemberList):
    """
    This class handles database members.
    """
    type = 'databases'

    def __init__(self, supervisor):
        super(Databases, self).__init__(supervisor)
        exts = supervisor.exts
        self.databases = exts.databases = DatabaseContainer({})
        self.host = exts.config['database.host']
        self.port = exts.config['database.port']
        self.user = exts.config['database.user']
        self.password = exts.config['database.password']
        self.debug = True  # FIXME: get the value from a sane location

    def get_connection(self, dbname):
        """
        Get a connection object for a given database.
        """
        return Database.connect(dataase=dbname, host=self.host, port=self.port,
                                user=self.user, password=self.password,
                                debug=self.debug)

    def collect(self, component):
        migrations = component.get_export('migrations', default='migrations')
        databases = component.get_export('databases', default=[])
        for dbname in databases:
            migration_pkg = '{}.{}.{}'.format(component.name, migrations,
                                              dbname)
            self.register((dbname, migration_pkg, component.name))
            logging.debug('Registered database {} for {}'.format(
                dbname, component.name))

    def install_member(self, database):
        dbname, migrations_pkg, component_name = database
        dbconn = self.get_connection(dbname)
        dbconn.package_name = component_name
        self.databases[dbname] = dbconn
        migrate(dbconn, migrations_pkg, self.supervisor.config)
        self.event.publish(DATABASE_READY, name=dbname, db=dbconn)
        logging.info('Database {} installed for {}'.format(
            dbname, component_name))
