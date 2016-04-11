Components and component members
================================

Components are, simply put, subapplications. They have their own templates,
static assets, route handlers, database migrations, and so on. Each of these
things are called 'component members'. Some members may require load ordering
(e.g., plugins may depend on other plugins, some routes may require to be
registered after others or before others). We call these ordering requirements
'component member dependencies'.

Component member groups
-----------------------

Component member groups (CMGs) are groups of component members by type. We
currently have the following groups:

- databases
- templates
- static assets
- hooks
- plugins
- WSGI middleware
- route handlers
- command line argument handlers

Each component may have one or more members that belong to one of the CMGs. The
CMGs are also known as component member type. 

A single component group consists of all members of the same type from all
components. Although this may sound simple enough, it is worth keeping in mind
that it *is* possible to step on other component's assets/templates/databases
if you are not careful, as members are not namespaced. For example, if
component A has a template named 'foo', and component B also has that template,
the last component's template will always take precedence and override any
previously found templates of the same name. Also, keep in mind that overriding
templates in this way *intentionally* is also a bad idea, as the override order
is an implementation detail that may change in future without notice.

Component configuration file
----------------------------

Each component has a configuration file. This configuration file is in .ini
format. By default, the configuration files will be looked up in 'config.ini'
inside the package. A different location can be specified in the package's
``__init__`` module by adding a :py:data:`CONFIG` constant. For example::

    # mycomponent/__init__.py
    CONFIG = 'configs/mycomponent.ini'

This path is relative to the package directory and follows the same rules as
the paths declared elsewhere in the configuration file itself: cannot contain
double-dots, cannot be an absolute path, and so on.

The component member exports are specified in the ``[exports]`` section of the
configuration file.

In the following subsections, we will repeat the section header every time, but
do keep in mind that all exports go under a single ``[exports]`` heading.

.. note::
    The exact format used in the configuration files is covered `in confloader
    module documentation
    <http://confloader.readthedocs.org/en/latest/writing_ini.html>`_.

Object and path references
~~~~~~~~~~~~~~~~~~~~~~~~~~

When specifying relative paths in the configuration options, you cannot use
double-dot notation anywhere. For example, ``static_dir = ../foo`` is not
allowed. The path resolver code will automatically strip out the ``../`` part.
The paths are always resolved relative to the package directory and must point
to locations within it.

When referring to objects (functions, classes, etc), Python name in dotted path
format is used (e.g., ``hooks.on_initialize``). These names are resolved
relative to the component's package (the package is prefixed to the name before
importing). Multiple dots will be treated as a single dot, and any leading dots
will be stripped. The names must point to importable objects. In most cases,
failure to import an object will result in omission of that object.

Options with mutiple values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some options allow one or more values. For a single value we write::

    option = value

For multiple values, we use a slightly different format::

    option =
        value 1
        value 2

Remember to add a newline before the first value and indent all lines until the
next option. Each line is treated as a separate value.

Databases
---------

Components can use one or more databases. Use of a database is completely
optional, and components that do not specify any databases will not have them.

There are two configuration options that are used for configuring databases::

    [exports]

    databases = mycomponent

    migrations = migrations.package

If a components wants to use a database, the first option is required. The
``databases`` option can be used to specify one or more database that the
component wants to use.

The ``migrations`` option is used to point to a Python package that contains
database migrations. This option is optional, and the default value is
``migrations``. The package names are resolved relative to the component's
package name. The package must contain subpackages that match the database
name(s).

For more information on working with databases, see
:doc:`working_with_databases`.

.. warning::
    Try to pick a database name that will be reasonably unique across
    components.

Templates
---------

By default, templates used in a component are looked for in a directory called
'views', located inside the component's package directory. This can be changed
by specifying one or more alternative locations. For example::

    [exports]

    templates = templates

It is important to remember that templates are resolved relative to template
directories, regardless of how many leaves of hierarchy there is between the
package directory and the template directory.

To illustrate template resolution, let's take a look at a concrete example.
Let's say the directory layout is as follows::

    package/
        templates/
            foo/
                foo1.tpl
                foo2.tpl
            bar/
                baz/
                    baz1.tpl
                    baz2.tpl
                bar1.tpl
                bar2.tpl

With this structure, let's take a look at what would happen if your
configuration looked like this::

    [exports]

    tempates =
        templates/foo
        templates/bar

If we ask for a template named 'foo1', it will be found at
'templates/foo/foo1.tpl'. If we ask for 'foo/foo1', it will not be found,
because neither 'foo' or 'bar' directories have a subdirectory called 'foo'.
Asking for 'baz/baz1' will match 'templates/bar/baz/baz1'.

On the other hand, if our configuration looked like the example at the top of
this subsection, 'foo1' would not resolve, while 'foo/foo1' would work.

For more information on working with templates, see
:doc:`working_with_templates`.

.. warning::
    Try to make template names unique, as templates may step on each other. If
    two components define templates that are named the same, they will override
    each other in unpredictable ways.

Static assets
-------------

Before we talk about configuration options for static assets, we must
understand that there are two kinds of static assets. We differentiate between
*source assets* and *bundles*. 

Source assets are files that are found inside the static assets directory,
while bundles are collections of source assets that are bundled (concatenated)
together to form the final timestamped file that will be used in the templates.
Furthermore, bundles are generated on the fly, and only the source files are
required to be present in the source tree.

Options related to static assets are used to specify the directory where the
source files are kept, and enumerate the JavaScript and CSS bundles that your
component needs.

By default, the source assets are looked up in ``static`` directory within the
package directory. To change this behavior, we can use the ``static_dir``
option. ::

    [exports]

    static_dir = assets

.. note::
    The static directory is expected to contain 'js' and 'css' subdirectories.
    There is currently no way to change this.

Bundles are defined using two options::

    [exports]

    js_bundles =
        article: autoscroll, comment
        summary: autoscroll, imagebox

    css_bundles =
        article: article_layout
        summary: summary_layout

This configuration creates two JavaScript bundles, and two CSS bundles. The
JavaScript bundle 'article' contains concatenated and minified sources of
'static/js/autoscroll.js' and 'static/js/comment.js'. As you can see, the
static assets directory and 'js/' subdirectory are automatically added to the
name, as is the '.js' extension.

For more information on working with static assets, see
:doc:`working_with_static_assets`.

.. warning::
    Note that using bundle names that are defined in other components will
    cause the bundles to be merged and the source assets from those bundles
    will be concatenated in the order the components themselves are registered.

Hooks
-----

Hooks are functions that are executed for events. In context of component
exports, these events are system events emitted by the supervisor.

Every function that is going to be used as a hook must be decorated with a
:py:func:`~librarian.core.exports.hook` decorator. ::

    from librarian.core.exports import hook

    @hook('initialize')
    def on_initialize(supervisor):
        # do something when component is initializing...

Any of the system and custom events can be used. For the full list of events
and their meaning, see :doc:`../appendices/list_of_system_events`.

Of these, actually useful ones are probably 'initialize',
'component_member_loaded', 'init_complete', and 'background'. The 'background'
even is interesting in particular, as it allows the component to repeatedly
execute code on an interval. More information on event handling and supervisor
hooks can be found in :doc:`working_with_events`.

Once we have the decorated functions, we can list them in the configuration
file using the ``hooks`` option::

    [exports]

    hooks = hooks.on_initialize

In this case, we have an ``on_initialize`` function in a ``hooks`` module.

Plugins
-------

Plugins are classes and functions that follow the `Bottle's plugin API
<http://bottlepy.org/docs/dev/plugindev.html>`_. Just like middleware, plugins
are applied in order like an onion skin. The last plugin that is registered is
applied first, and the first plugin registered will be applied last. The
request is intercepted by the last (outermost) plugin, and is passed through
down the chain to the innermost plugin, which hands it over to the actual
request handler. ::

    plugins:        p1   p2   p3   p4   |
                    |    |    |    |    |
    reuqest  --->---+----+----+----+----+--\
                    |    |    |    |    |  |  request handler
    response ---<---+----+----+----+----+--/
                    |    |    |    |    |

The above diagram graphically shows the way plugin code is executed. In terms
of Python code, you can think of it has having multiple decorators applied to
the handler function, where the first plugin that is registered is the first
decorator::

    @plugin1
    @plugin2
    @plugin3
    @plugin4
    def handler():
        pass

Because of the way plugins work, the order in which they are registered becomes
import. Plugin registration, therefore, supports dependency declaration.

.. note::
    Dependency/dependents declaration is completely optional. It is only needed
    if order matters. If you are reasonably sure that it does not matter where
    in the stack your plugin is executed, you may skip to the end of this
    subsection.

Plugins can declare dependencies on each other using
:py:func:`~librarian.core.exports.depends_on` and
:py:func:`~librarian.core.exports.required_by` decorators. For semantic
clarity, these two decorators have aliases, which are
:py:func:`~librarian.core.exports.after` and
:py:func:`~librarian.core.exports.before`, respectively. 

Alternatively, plugins may have :py:attr:`depends_on` and
:py:attr:`required_by` attributes (if, for example, your plugin is a class).
These attributes are the equivalent to
:py:func:`~librarian.core.exports.depends_on` and
:py:func:`~librarian.core.exports.required_by` decorators, respectively.

Here are a few examples::

    import functools

    from librarian.core.exports import *

    
    @depends_on('foo')
    def my_plugin(handler):
        ....
    my_plugin.name = 'myawesomeplugin'

    @before(['bar', 'baz'])
    def my_other_plugin(handler):
        ....
    my_other_plugin.name = 'myfantasticplugin'


    class MyPlugin(object):
        name = 'myexcuisiteplugin'
        api = 2
        depends_on = ['foo', 'bar']
        required_by = 'baz'

        def __call__(self, handler):
            ....

Note that each plugin has a ``name`` attribute. This name is used to identify
the plugin, and this is the name that is used to refer to other plugins in the
dependency/dependents declaration decorators and attributes. Also note that the
dependency/dependents declaration can be a single string, or a list of strings.

Once we have our plugins with dependencies we enumerate them in the exports::

    [exports]

    plugins = plugins.my_plugin

We can specify one or more plugins in the ``plugins`` option.

The values are names of the plugin functions or classes in dotted path format
(e.g., what we would use in an import), and are resolved with component's
package name prepended. In the example, we have a ``my_plugin`` function in the
``plugins`` module. The ``plugins`` module itself is expected to be found in
the component package.

For a complete list of plugins that are used in Librarian, please refer to
:doc:`../appendices/list_of_librarian_plugins`.

WSGI middleware
---------------

WSGI middleware follow the same rules as plugins. Unlike plugins, though, WSGI
middleware do not have a ``name`` attribute, and are referred to by their full
module path (e.g., ``librarian.core.i18n.I18NMiddleware``).

Declaring in the configuration is done using the ``middleware`` option, listing
one or more names of the middleware classes::

    [export]

    middleware = 
        middleware.HeroicMiddleware
        middleware.FantasticMiddleware

Route handlers
--------------

When it comes to route handlers, there are two things to keep in mind.

- Librarian uses class-based route handlers which have their own registration
  methods and properties
- routes may be subject to dependency resolution just like plugins and
  middleware

For more information on class-based route handlers, see
:doc:`handling_requests`.

Dependencies are declared by adding :py:attr:`depends_on` and
:py:attr:`required_by` attributes to the route class. These attributes can
refer to one or more route names. The route names are defined on the classes.

.. note::
    The dependency and dependents declarations only determine the order in
    which route handlers are *registered* and not the order in which they are
    *matched*. The latter is determined by the path pattern and Bottle's
    routing algorithm.

Here is an example::

    from streamline import RouteBase


    class MyRoute(RouteBase):
        name = 'mycomponent:myroute'
        depends_on = 'files:list'

The above example declares ``MyRoute``'s dependency on ``'files:list'``.

To declare route handlers and have them registered, we use the ``routes``
option in the exports. One or more names of the route handler classes can be
used::

    [exports]

    routes =
        routes.MyRoute
        routes.YourRoute

.. warning::
    Be careful about how you name the routes. Names are not guaranteed to be
    unique across the entirety of Librarian and any external components.

Command line argument handlers
------------------------------

Command line argument handlers are functions that can handle arbitrary
user-defined arguments. To mark a function as a command handler, you need to
use the :py:func:`~librarian.core.exports.command` decorator. Here is an
example::

    from librarian.core.exports import command

    @command('awesome', '--make-awesome', action='store_true')
    def awesome_command(args):
        ....

The first argument to the decorator is the command name, which is used to
tell if the command should run. The second argument is a flag that is used on
the command line to invoke this command. Other arguments are passed as is to
the :py:meth:`argparse.ArgumentParser.add_argument` method.

A command may register additional arguments that it wants to use. These
arguments are specified as an iterable of dicts, where each dict is a set of
keyword arguments for the :py:meth:`~argparse.ArgumentParser.add_argument`
method. For example::

    extras = (
        dict(flags=['--awesome-level', '-L'], metavar='LEVEL', default=2]),
        dict(flags=['--ignore-lame', '-I'], action='store_true'),
    )

    @command('awesome', '--make-awesome', extra_args=extras,
             action='store_true')
    def awesome_command(args):
        ...

The above example adds '--awesome-level' and '--ignore-lame' arguments. Note
that flags can be either a single string, or a list of strings.

The command line argument handlers can also be written as classes as well. The
arguments passed to the :py:func:`~librarian.core.exports.command` decorator
can be written as attributes on the class. The command handler class must also
implement a :py:meth:`run` method which is invoked with an object containing
parsed command line arguments arguments as its own argument. For example::

    class AwesomeCommand(object):
        name = 'awesome'
        flags = '--make-awesome'
        ation = 'store_true'

        def run(self, args):
            ....

To find out more about writing command handlers, see
:doc:`command_line_arguments`.

To export handlers, we use the ``commands`` options in the exports section::

    [exports]

    commands = commands.fantastic_command

The option accepts one or more names of the function objects.

.. warning::
    Command names have to be unique across all commands in the commands member
    group. If a command has the same name as another command, it will not be
    used.

Further reading
---------------

All of the exported component members are collected by collectors. If you wish
to find out more about the collector API and writing your own collectors, see
:doc:`writing_component_member_collectors`.
