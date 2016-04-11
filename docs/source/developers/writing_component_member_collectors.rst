Writing component member collectors
===================================

Before a component can become part of the application, it needs to declare all
of its moving and non-moving parts and have them collected and installed. For
more information on the particulars of declaring (or 'exporting') these parts,
please read the :doc:`component_exports` section.

Overview of component member collection and installation
--------------------------------------------------------

The component members are collected and installed by group. For each group
(databases, hooks, commands, etc), the exports manager performs a collect on
all components, followed by install, again on all components. This means that
each group is fully processed before the next one.

The collection and installation of component member groups is performed by
collector classes. The particulars of collection and installation are
completely up to the individual collector implementation. What is common for
all collectors, though, is the fact that they are resilient to exception raised
during the process. In all cases, exceptions are silenced and logged. This
ensures that the application will start even if a misbehaving component member
is present in any of the components.

Requirements for the collected objects
--------------------------------------

Because collectors are fairly generic, they may impose expectations on the
collected objects. In fact, whether something is a Python object, or a file or
a folder on the disk, is also such an expectation. The author of the collector
class must set the rules and (optionally) provide the tools to meet them.

A good example of the requirements a collector may impose is that command
handlers must have a ``name`` attribute. Because the collectors API expects
that no exception can cause the process to break, there are no APIs for
enforcing these rules. Therefore, for some of the rules, other then documenting
them, the author may not need to do anything.

Writing collector classes
-------------------------

There are three base classes for concrete collector classes. The
:py:class:`~librarian.core.exports.Collector` class is the most rudimentary
class. We will not use this class in the examples as there is normally no need.

The other two classes are :py:class:`~librarian.core.exports.ListCollector` and
:py:class:`~librarian.core.exports.DependencyCollector`. The primary difference
between these two is that the latter imposes an additional requirement on the
exported members that they must have ``depends_on`` and/or ``required_by``
attributes if they wish to be subject to dependency resolution. 

.. note::
    If none of the members have dependencies declared, the
    :py:class:`~librarian.core.exports.DependencyCollector` collectors behave
    the same way as the :py:class:`~librarian.core.exports.ListCollector`
    collectors, but less efficiently.

In general, the concrete collector classes need to implement two methods:

- ``collect(component)``
- ``install_member(collected_member)``

The ``collect()`` method obtains information about members that the collection
exports, and collects all members belonging to the component. The process of
collection results in a list of installation candidates and prepares the
candidates for installation (e.g., imports objects, etc). For each installation
candidate, the method must call ``register()``.

The ``install_member()`` method installs a single member. The term 'install'
should be interpreted very broadly (perhaps 'activate' or 'register' may better
describe it in some instances), and performs the task of making the member
usable to the application.

Example collector
-----------------

For our example, we will assume that our application has a central 'state'
registry. This registry maintains arbitrary state information and allows the
components to update the state on interval.

The members that update the state will have the following requirements:

- They must give the update interval in increments of 5 seconds as ``interval``
  attribute.
- They must have an ``update()`` method that calculates the new state and
  returns a dict.
- They must have a ``namespace`` attribute that provides the namespace for the
  state information.

The state member do not depend on each other, so we will use the
:py:class:`~librarian.core.exports.ListCollector` as our base class. ::

    from librarian.core.exports import ListCollector


    class State(ListCollector):
        pass

Now let's implement the ``collect()`` method. The members will be listed under
the ``state`` option in the ``[exports]`` section of the component
configuration. ::

    import logging
    from librarian.core.utils import to_list
    ...

    class State(ListCollector):
        def collect(self, component):
            updaters = to_list(component.get_export('state', []))
            for u in updaters:
                try:
                    updater = component.get_object(u)
                except ImportError:
                    logging.error('Failed to import updater %s', u)
                    continue
                self.register(updater)

The component's :py:meth:`~librarian.core.exports.Component.get_export` method
returns the value of the ``state`` option. Not all components will have state 
updaters so we specify that we want an empty list as the default value. Since
we wish to allow either a single string or a list of strings to be used, we
call the :py:func:`~librarian.core.utils.to_list` function to ensure we have a
list regardless of which value is in the configuration.

We iterate over the exported members and we try to load the object using the
component's :py:meth:`~librarian.core.exports.Component.get_object` method.
This method raises an :py:exc:`ImportError` if the object cannot be imported,
so we catch it and log it. We allow the iteration to continue to give any of
the other members to successfully register.

Finally, we register the imported object using the
:py:meth:`~librarian.core.exports.Collector.register` method.

In fact, what we just did is so common, that there is already a mixin that does
it for us, and we just wasted a lot of time writing it from scratch... ::

    from libraian.core.exports ObjectCollectorMixin
    ....

    class State(ObjectCollectorMixin, ListCollector):
        exports_key = 'state'

We will now implement the install part. Before we do that, though, we need to
create the instance of application state class (just imagine it exists). ::

    from mystate import State as AppState
    ...

    class State(ObjectCollectorMixin, ListCollector):
        def __init__(self, supervisor):
            super(State, self).__init__(supervisor)
            self.state = self.supervisor.ext.state = AppState()
        ...

With the last change, we've added the application state object to the collector
class so that we can use it during installation. Now we can go on to implement
the ``install_member()`` method itself. ::

    ...

    class State(ObjectCollectorMixin, ListCollector):
        ...
        def install_member(self, updater):
            self.state.add_updater(updater)

Hopefully this wasn't so difficult. But what if we wanted to make sure nobody
could export an updater that has not met the requirements we defined before?
One way to do it is check during collect. An equally valid place to do this is
just before installing. In our case, it looks simpler to do it before install.
Here is the updated code::

    from librarian.core.utils import hasmethod
    ...

    class State(ObjectCollectorMixin, ListCollector):
        ...
        def install_member(self, updater):
            requirements = [
                hasmethod(updater, 'update'),
                hasattr(updater, 'interval'),
                hasattr(updater, 'namespace'),
            ]
            if not all(requirements):
                logging.error('Invalid updater %s', updater)
                return
            self.state.add_updater(updater)

This concludes our example.

Further reading
---------------

For more information on collector API and classes mentioned in this tutorial,
please refer to the API documentation for the 
:doc:`../api/librarian.core.exports` module.
