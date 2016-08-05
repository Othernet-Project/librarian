import functools
import uuid

from ...core.exts import ext_container as exts


class StateContainer(object):
    """
    Keeps a registry of all installed :py:class:`StorageProvider` instances
    and references to all the data that they manage.
    """
    #: Unique identifier of event which notifies about state changes
    STATE_CHANGED_EVENT = 'state_changed'
    #: Name of the state container object (used when generating the cache key)
    name = 'state'
    #: Template used to generate cache keys for each provider
    key_template = '{name}-{id}-{provider}'

    def __init__(self, **kwargs):
        self._registry = kwargs.get('registry', dict())
        self._cache = kwargs.get('cache', exts.cache)
        self._events = kwargs.get('events', exts.events)
        self._id = uuid.uuid4().hex
        self._changed = set()

    def __get_key(self, provider):
        """
        Return a unique key under which the passed in ``provider`` can store
        it's data.
        """
        return self.key_template.format(name=self.name,
                                        id=self._id,
                                        provider=provider)

    def __get(self, key):
        """
        Callback function invoked by :py:class:`StorageProvider` instances when
        they query for their data.
        """
        return self._cache.get(key)

    def __set(self, provider_name, key, data, timeout):
        """
        Callback function invoked by :py:class:`StorageProvider` instances when
        they store their data.
        """
        self._cache.set(key, data, timeout=timeout)
        # add key to set of keys that were changed since last synchronization
        self._changed.add(provider_name)
        # emit event notifying potential subscribers about a single change.
        # subscriber is passed only the provider object, not the data itself,
        # to enforce the same access methods and permissions as with getters
        # and setters, avoiding access violations (if left untreated) or the
        # need for additional checks in the subscriber code (if data was
        # passed directly)
        provider = self._registry[provider_name]
        self._events.publish(self.STATE_CHANGED_EVENT, provider=provider)

    def __onchange(self, provider_name, callback):
        """
        Callback function invoked by :py:class:`StorageProvider` instances to
        subscribe the passed in `callback` to change events of `provider_name`.
        """
        condition = lambda event, provider: provider.name == provider_name
        self._events.subscribe(self.STATE_CHANGED_EVENT,
                               callback,
                               condition=condition)

    def __getattr__(self, name):
        """
        Shorthand for getting the provider and calling it's ``get`` method.
        """
        return self._registry[name].get()

    def __getitem__(self, name):
        """
        Shorthand for getting the provider and calling it's ``get`` method.
        """
        return self._registry[name].get()

    def provider(self, name):
        """
        Return a storage provider instance specified by ``name``.
        """
        return self._registry[name]

    def register(self, provider_cls):
        """
        Register a new storage provider instance.

        Raises :py:exc:`ValueError` if a provider with the same name already
        exists.
        """
        if provider_cls.name in self._registry:
            raise ValueError("A StorageProvider with '{}' name already"
                             " exists".format(provider_cls.name))
        # pass getter, setter and subscriber functions to the constructor of
        # providers, which they use to store and query their data or subscribe
        # to changes
        key = self.__get_key(provider_cls.name)
        # some of the parameters are bound ahead-of-time so providers don't
        # have a possibility to change them
        getter = functools.partial(self.__get, key)
        setter = functools.partial(self.__set, provider_cls.name, key)
        onchange = functools.partial(self.__onchange, provider_cls.name)
        instance = provider_cls(getter=getter,
                                setter=setter,
                                onchange=onchange)
        self._registry[provider_cls.name] = instance

    def fetch_changes(self):
        """
        Return a dict containing references to the providers which data has
        changed since the last call to it.
        """
        changed = self._changed
        # ensure atomicity
        self._changed = set()
        return dict((k, self._registry[k]) for k in changed)
