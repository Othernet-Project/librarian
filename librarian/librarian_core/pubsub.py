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

    def publish(self, event, *args, **kwargs):
        """Publish an event with arbitary arguments. All the subscriberes of
        the particular event will be invoked with the passed in arguments.

        :param event:  unique string identifier of the event
        """
        listeners = self._subscribers.get(event, [])
        for listener in listeners:
            listener(*args, **kwargs)

    def subscribe(self, event, listener):
        """Register a callback function for a specific event.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        """
        subscribers = self._subscribers.setdefault(event, [])
        if listener not in subscribers:
            subscribers.append(listener)

    def unsubscribe(self, event, listener):
        """Unregister a callback for a specific event type.

        :param event:     unique string identifier of the event
        :param listener:  a callable object
        """
        subscribers = self._subscribers.get(event, [])
        if listener in subscribers:
            subscribers.remove(listener)

    def get_subscribers(self, event):
        """Returns a copy of the list of subscribers to a specific event type.
        The list is cloned only to protect from eventual attempts of manually
        modifying the list, as it would be possible if the reference to the
        orignal list were to be returned.

        :param event:     unique string identifier of the event
        """
        return list(self._subscribers.get(event, []))
