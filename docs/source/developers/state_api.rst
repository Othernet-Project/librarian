State API
=========

The State API provides a globally accessible container (through the extension
container facility, i.e. ``exts.state``) to share data between unrelated
components through data providers.


Providers
---------

Data providers are used to manage access to read and write operations of the
data governed by them. Users of the state API may implement any number of data
providers by subclassing :py:class:`~librarian.data.state.provider.StateProvider`
for each data source.

Through class attributes on these providers, it is possible to specify the
allowed access modes to the data (read-only, write-only or read-write), the
timeout value of the data (which when expires, invalidates the data) and a
default value in case the provider has no associated data at all.

Further customization is allowed by overriding it's methods, which most of all
can be used to implement fine-grained permission restrictions to the data. These
permission checks (as well as access mode checks) are performed on every access
to the provider's data.

A sample provider implementation could look like this::

    from bottle import request

    from librarian.data.state.provider import StateProvider

    class SeasonProvider(StateProvider):
        name = 'season'
        allowed_modes = 'rw'  # this is the default
        timeout = 0  # no timeout
        default_value = 'uncertain'

        def has_write_permission(self):
            return request.user.is_superuser

This is sufficient for a provider to be accepted as valid (though except a name,
nothing else is actually required), and then it just needs to be declared in the
exports section of the component, so the state provider collector can register
it on application startup::

    [exports]
    state =
        seasons.SeasonProvider

Thus the provider can be accessed through the extension container as::

    provider = exts.state.provider('season')
    assert provider.get() == 'uncertain'

Provided that the current user is logged in and is a super-user::

    provider.set('summer')
    assert provider.get() == 'summer'

Some additional convenience methods are also publicly accessible to perform
checks before attempting data access, like::

    assert provider.is_readable()
    assert provider.is_writeable()
    assert provider.has_read_permission()
    assert provider.has_write_permission()

    request.user.logout()

    assert not provider.has_write_permission()

Providers utilize the existing pub-sub system to deliver updates to subscribers
about changes to the underlying data. To subscribe to changes over the provider::

    def season_changed(event, provider):
        print(provider.get())

    provider.onchange(callback)

Instead of passing the new data to the callback function, the provider instance
itself is being passed as the only argument (aside from the event id) in order
to be able to enforce the same access restrictions on anyone who may get access
to the arguments of the subscriber function.


Containers
----------

Ideally there's no need for multiple container instances, and within librarian
there is only one single instance of it attached onto the extension container.
It allows users of it to get access to individual providers or to register new
ones. As it's also being exposed within templates to give them access to the
data of providers, both ``__getitem__`` and ``__getattr__`` magic methods of the
container delegate their calls to the matching (by name) provider's ``get``
method (just for convenience)::

    assert exts.state.season == 'summer'
    assert exts.state['season'] == 'summer'

This is because actual access to the provider itself is less often needed than
read access to the underlying data, so getting the provider instance is possible
only using the :py:meth:`~librarian.data.state.container.StateContainer.provider`
method.

Registering a new provider is as simple as calling one single method::

    exts.state.register(SeasonProvider)

which could be useful if the static nature of provider installation through the
exports system doesn't prove to be flexible enough.

The container's ``fetch_changes`` method is used to get a mapping of provider
names and provider instances which data has been changed since the last call to
the same method. This effectively means that periodic calls to ``fetch_changes``
can be used to get only the differences in the data, thus synchronization of all
the data is rarely (if ever) needed.


Client Side
-----------

The client side javascript API tries to match the Python backend API as much as
possible, but there are subtle differences of course. ``window.state``
represents the state container object, and accessing provider names on it
directly has the same effect as in the backend (delegating the call to the
provider's ``get`` method), while the special ``provider`` method gives access
to provider instances themselves.

The client side synchronizer code performs periodic ajax requests towards an
endpoint that essentially returns a JSON object containing the results of
``fetch_changes`` and updates the providers with the data that came in. Updating
the data this way triggers the callbacks registered on the provider(s) to notify
interested parties about the change of data on the provider in question. Just
like in the backend code, the callbacks are passed the provider instance itself,
instead of the raw data.::

    callback = (provider) ->
      console.log provider.get()

    window.state.season.onchange(callback)

In case additional postprocessing is needed over the data (whether it needs to
replace the exising one or update it with additional calculated values, such
postprocessors can be registered this way::

    appender = (data) ->
      data + ' is awesome'

    provider = window.state.provider 'season'
    provider.postprocessor appender

Using such a postprocessor, the value returned by it will be used as-is, to
replace the source data that was passed to it, so the provider itself will contain
only the newly generated value.

In case complex objects are being stored by the provider, it is possible to
only partially update the underlying data without completely replacing it, but
it needs an additional argument when registering the postprocessor that
represents a sequence of keys that needs to be followed so only the data that it
points to in the data structure will be replaced by the return value of the
postprocessor.::

    calculator = (data) ->
      data.x + data.y

    provider = window.state.provider 'addition'
    provider.postprocessor calculator 'result'
    provider.set { x: 1, y: 3 }

The above example will result with the provider storing an object with one
additional key::

    { x: 1, y: 3, result: 4}

Nested objects are also managable::

    calculator = (data) ->
      data.x + data.y

    provider = window.state.provider 'addition'
    provider.postprocessor calculator ['result', 'x+y']
    provider.set { x: 1, y: 3, result: {} }

Which would result in an object such as::

    { x: 1, y: 3, result: { 'x+y': 4} }


Data binding
------------

On top of the above described synchronizer lies the data binding mechanism. It
does not contain any control constructs, such as loops or conditionals, only
direct binding of data as text, html, or as some attribute on html elements. The
data source is recognized by the binding mechanism from the provided binding
expression and the binder automatically subscribes to changes from the detected
data source(provider) for the specific element that it targets. This way not all
bindings need to be refreshed during any update of any provider, but only those
that are subscribed to the changes.::

    <p data-bind="text: addition.x"></p>
    <div data-bind="id: addition.y + '-unique'"></div>
    <span data-bind="style: {width: addition.x + 'px'}"></span>
