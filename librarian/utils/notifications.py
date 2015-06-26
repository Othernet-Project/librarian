"""
notifications.py: Notification system

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import functools
import uuid

from bottle import request
from bottle_utils.common import unicode


NOTIFICATION_COLS = (
    'notification_id',
    'message',
    'category',
    'icon',
    'priority',
    'created_at',
    'read_at',
    'expires_at',
    'dismissable',
    'user',
)


class Notification(object):
    NORMAL = 0
    URGENT = 1
    CRITICAL = 2
    PRIORITIES = (NORMAL, URGENT, CRITICAL)

    def __init__(self, notification_id, message, created_at, category=None,
                 icon=None, priority=NORMAL, expires_at=None, dismissable=True,
                 read_at=None, user=None):
        self.notification_id = notification_id
        self.message = unicode(message)
        self.created_at = created_at
        self.category = category
        self.icon = icon
        self.priority = priority
        self.expires_at = expires_at
        self.dismissable = dismissable
        self._read_at = read_at
        self.user = user

    @classmethod
    def send(cls, message, category=None, icon=None, priority=NORMAL,
             expiration=0, dismissable=True, user=None, group=None):
        # TODO: if group is not None, query all users of the specified group
        # and create a notification instance for each member of the group
        instance = cls(notification_id=cls.generate_unique_id(),
                       message=message,
                       created_at=datetime.datetime.now(),
                       category=category,
                       icon=icon,
                       priority=priority,
                       expires_at=cls.calc_expiry(expiration),
                       dismissable=dismissable,
                       read_at=None,
                       user=user)
        instance.save()

    @property
    def has_expired(self):
        return (self.expires_at is not None and
                self.expires_at < datetime.datetime.utcnow())

    @property
    def is_shared(self):
        return not self.user

    @property
    def read_at(self):
        if self.is_shared:
            read_data = request.user.options.get('notifications', {})
            return read_data.get(self.notification_id, None)

        return self._read_at

    @property
    def is_read(self):
        return self.read_at is not None

    def _mark_shared_read(self, read_at):
        if 'notifications' not in request.user.options:
            request.user.options['notifications'] = dict()

        request.user.options['notifications'][self.notification_id] = read_at

    def _mark_private_read(self, read_at):
        db = request.db.sessions
        query = db.Update('notifications',
                          read_at=':read_at',
                          where='notification_id = :notification_id')
        db.query(query,
                 notification_id=self.notification_id,
                 read_at=read_at)
        self._read_at = read_at

    def mark_read(self, read_at=None):
        read_at = datetime.datetime.now() if read_at is None else read_at
        if not self.is_read:
            if self.is_shared:
                # shared notifications store the datetime of reading in the
                # user's session
                self._mark_shared_read(read_at)
            else:
                # only personal notifications can be marked as read in the db
                self._mark_private_read(read_at)

        return self

    def save(self):
        db = request.db.sessions
        query = db.Replace('notifications', cols=NOTIFICATION_COLS)
        db.query(query,
                 notification_id=self.notification_id,
                 message=self.message,
                 created_at=self.created_at,
                 category=self.category,
                 icon=self.icon,
                 priority=self.priority,
                 expires_at=self.expires_at,
                 dismissable=self.dismissable,
                 read_at=self._read_at,
                 user=self.user)
        return self

    def delete(self):
        db = request.db.sessions
        query = db.Delete('notifications', where='notification_id = ?')
        db.query(query, self.notification_id)
        return self

    @staticmethod
    def generate_unique_id():
        return uuid.uuid4().hex

    @staticmethod
    def calc_expiry(expiration):
        if expiration == 0:
            return None

        return datetime.datetime.utcnow() + datetime.timedelta(expiration)


class NotificationGroup(object):

    proxied_attrs = (
        'created_at',
        'expires_at',
        'read_at',
        'is_read',
        'dismissable',
        'icon',
        'category',
        'priority',
    )

    def __init__(self, notifications=None):
        self.notifications = notifications or []

    def __getattr__(self, name):
        if name in self.proxied_attrs:
            try:
                return getattr(self.notifications[0], name)
            except IndexError:
                raise ValueError('Notification group has 0 notifications.')

        return super(NotificationGroup, self).__getattr__(name)

    def add(self, notification):
        self.notifications.append(notification)

    @property
    def count(self):
        return len(self.notifications)

    def is_similar(self, notification, attrs):
        """Returns whether `notification` is similar to existing members of the
        group or not."""
        are_equal = lambda n: getattr(notification, n) == getattr(self, n)
        return all([are_equal(attr_name) for attr_name in attrs])

    @classmethod
    def group_by(cls, notifications, by):
        """Return list of notification groups, grouped by the `by` param.

        :param notifications:  iterator yielding `Notification` objects
        :param by:             tuple containing names of attributes to use in
                               similarity comparison.
        """
        group_list = []
        try:
            group = cls([next(notifications)])
        except StopIteration:
            return group_list
        else:
            group_list.append(group)
            for notification in notifications:
                if not group.is_similar(notification, attrs=by):
                    group = cls()
                    group_list.append(group)

                group.add(notification)

            return group_list


def to_dict(row):
    return dict((key, row[key]) for key in row.keys())


def get_notifications(notification_ids=None):
    """Return all those notifications that the current user has access to. If
    `notification_ids` is specified, the result set will be further limited to
    the specified ids."""
    db = request.db.sessions
    user = request.user.username if request.user.is_authenticated else None
    notification_ids = notification_ids or []

    query = db.Select(sets='notifications', where='user IS NULL')
    args = []
    if user:
        query.where |= 'user = ?'
        args += [user]

    if notification_ids:
        query.where += db.sqlin.__func__('notification_id', notification_ids)
        args += notification_ids

    db.query(query, *args)
    return (Notification(**to_dict(row)) for row in db.results)


def notifies(message, **params):
    """Decorator that creates a notification upon the successful return of it's
    wrapped function. E.g.:

    @notifies("They're together",
              category="joined",
              user=lambda: request.user.username)
    def join(a, b):
        return a + b

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if request.app.exts.is_installed('notifications'):
                options = dict((name, value() if callable(value) else value)
                               for name, value in params.items())
                Notification.send(message=message, **options)

            return result
        return wrapper
    return decorator


def notification_plugin(app):
    app.exts.notifications = Notification
