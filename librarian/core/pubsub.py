"""
pubsub.py: Simple Pub/Sub mechanism

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


DEFAULT_CONDITION = lambda *args, **kwargs: True


class PubSub(object):

    def __init__(self):
        self._subscribers = dict()
        self._scopes = dict()

    def _get_scope(self, fn):
        """Determine the scope of the passed in function."""
        while not hasattr(fn, '__module__'):
            fn = fn.func
        return fn.__module__

    def _is_within_scope(self, fn, scope):
        """Determine whether the passed in function is within the passed in
        scope."""
        try:
            found_scope = self._scopes[id(fn)]
        except KeyError:
            return False
        else:
            return found_scope.startswith(scope)

    def publish(self, event, *args, **kwargs):
        """Publish an event with arbitary arguments. All the subscriberes of
        the particular event will be invoked with the passed in arguments.

        :param event:  unique string identifier of the event
        :param scope:  scope to which event emission should be limited
        """
        scope = kwargs.pop('scope', None)
        listeners = self._subscribers.get(event, [])
        for (listener, condition) in listeners:
            within_scope = not scope or self._is_within_scope(listener, scope)
            if within_scope and condition(event, *args, **kwargs):
                listener(*args, **kwargs)

    def subscribe(self, event, listener, condition=DEFAULT_CONDITION):
        """Register a callback function for a specific event.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        :param condition: a callable object which is used to filter events
        """
        subscribers = self._subscribers.setdefault(event, [])
        if (listener, condition) not in subscribers:
            subscribers.append((listener, condition))
            self._scopes[id(listener)] = self._get_scope(listener)

    def unsubscribe(self, event, listener):
        """Unregister a callback for a specific event type.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        """
        subscribers = self._subscribers.get(event, [])
        subscribers[:] = [(l, cond) for (l, cond) in subscribers
                          if l is not listener]
        self._scopes.pop(id(listener), None)

    def get_subscribers(self, event):
        """Returns a copy of the list of subscribers to a specific event type.
        The list is cloned only to protect from eventual attempts of manually
        modifying the list, as it would be possible if the reference to the
        orignal list were to be returned.

        :param event:     unique string identifier of the event
        """
        return list(self._subscribers.get(event, []))
