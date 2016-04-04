"""
pubsub.py: Simple Pub/Sub mechanism

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


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
        return self._get_scope(fn).startswith(scope)

    def publish(self, event, *args, **kwargs):
        """Publish an event with arbitary arguments. All the subscriberes of
        the particular event will be invoked with the passed in arguments.

        :param event:  unique string identifier of the event
        :param scope:  scope to which event emission should be limited
        """
        scope = kwargs.pop('scope', None)
        listeners = self._subscribers.get(event, [])
        for listener in listeners:
            if not scope or self._is_within_scope(listener, scope):
                listener(*args, **kwargs)

    def subscribe(self, event, listener):
        """Register a callback function for a specific event.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        """
        subscribers = self._subscribers.setdefault(event, [])
        if listener not in subscribers:
            subscribers.append(listener)
            self._scopes[id(listener)] = self._get_scope(listener)

    def unsubscribe(self, event, listener):
        """Unregister a callback for a specific event type.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        """
        subscribers = self._subscribers.get(event, [])
        if listener in subscribers:
            subscribers.remove(listener)
            self._scopes.pop(id(listener), None)

    def get_subscribers(self, event):
        """Returns a copy of the list of subscribers to a specific event type.
        The list is cloned only to protect from eventual attempts of manually
        modifying the list, as it would be possible if the reference to the
        orignal list were to be returned.

        :param event:     unique string identifier of the event
        """
        return list(self._subscribers.get(event, []))
