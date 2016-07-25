from .exceptions import BadAccessMethod, AccessPermissionDenied


class StateProvider(object):
    """
    Provides access to a specific subset of state data.

    Whether the data is only readable, writeable, or both, can be specified
    by redefining :py:attr:`~StateProvider.allowed_modes` on the subclass,
    e.g.::

        allowed_modes = 'rw'
        allowed_modes = ('r', 'w')
        allowed_modes = 'w'

    In case readability and / or writeability of a provider can only be
    determined at runtime, subclasses may override the methods:

    - :py:meth:`~StateProvider.is_readable`
    - :py:meth:`~StateProvider.is_writeable`

    Finer-grained permissions can be achieved by overriding the methods:

    - :py:meth:`~StateProvider.has_read_permission`
    - :py:meth:`~StateProvider.has_write_permission`
    """
    #: Access mode definitions
    READ = 'r'
    WRITE = 'w'
    #: Unique identifier of a state provider object
    name = None
    #: Specify allowed access modes to state provider
    allowed_modes = (READ, WRITE)
    #: Default timeout value (0 - never times out)
    timeout = 0

    def __init__(self, getter, setter, onchange):
        if not self.name:
            raise ValueError("`name` not set")

        self._getter = getter
        self._setter = setter
        self._onchange = onchange

    def is_readable(self):
        """
        Return whether the provider supports read access to the underlying
        data or not.
        """
        return self.READ in self.allowed_modes

    def is_writeable(self):
        """
        Return whether the provider supports write access to the underlying
        data or not.
        """
        return self.WRITE in self.allowed_modes

    def has_read_permission(self):
        """
        Return whether the current read operation is permitted or not.
        """
        return True

    def has_write_permission(self):
        """
        Return whether the current write operation is permitted or not.
        """
        return True

    def get_timeout(self):
        """
        Return the timeout value for the data that's about to be stored.

        Leaving the default value of `0` means the data shall never expire.
        """
        return self.timeout

    def get(self):
        """
        Return data (if possible) that is managed by this provider.
        """
        # check access mode
        if not self.is_readable():
            raise BadAccessMethod("StateProvider '{}' does not support read"
                                  " access.".format(self.name))
        # check access permission
        if not self.has_read_permission():
            raise AccessPermissionDenied("StateProvider '{}' denied read"
                                         " access".format(self.name))
        # read and return data
        return self._getter()

    def set(self, data):
        """
        Store data (if possible) that is managed by this provider.
        """
        # check access mode
        if not self.is_writeable():
            raise BadAccessMethod("StateProvider '{}' does not support write"
                                  " access.".format(self.name))
        # check access permission
        if not self.has_write_permission():
            raise AccessPermissionDenied("StateProvider '{}' denied write"
                                         " access".format(self.name))
        # write data
        timeout = self.get_timeout()
        self._setter(data, timeout=timeout)

    def onchange(self, callback):
        """
        Convenience helper method that subscribes the passed in `callback`
        to the :py:attr:`~StateContainer.STATE_CHANGED_EVENT` event.
        """
        self._onchange(callback)
