"""
notifications.py: Notification system

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import uuid

from bottle import request


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
        self.message = message
        self.created_at = created_at
        self.category = category
        self.icon = icon
        self.priority = priority
        self.expires_at = expires_at
        self.dismissable = dismissable
        self.read_at = read_at
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
        return self.expires_at < datetime.datetime.utcnow()

    @property
    def is_shared(self):
        return not self.user

    def _is_shared_read(self):
        read_data = request.user.options.get('notifications', {})
        read_at = read_data.get(self.notification_id, None)
        if read_at:
            return read_at > self.created_at

        return False

    def _is_private_read(self):
        return self.read_at is not None

    @property
    def is_read(self):
        if self.is_shared:
            # shared notifications must be checked by date to find out whether
            # they have been read or not
            return self._is_shared_read()

        return self._is_private_read()

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
        self.read_at = read_at

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
                 created=self.created,
                 category=self.category,
                 icon=self.icon,
                 priority=self.priority,
                 expires=self.expires,
                 dismissable=self.dismissable,
                 read_at=self.read_at,
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
        return datetime.datetime.utcnow() + datetime.timedelta(expiration)


class NotificationGroup(object):

    def __init__(self, notifications):
        self.notifications = notifications

    @property
    def message(self):
        return self.notifications[0].message

    @property
    def created(self):
        return self.notifications[0].created

    @property
    def icon(self):
        return self.notifications[0].icon

    @property
    def priority(self):
        return self.notifications[0].priority


def to_dict(row):
    return dict((key, row[key]) for key in row.keys())


def get_notifications(notification_ids=None):
    """Return all those notifications that the current user has access to. If
    `notification_ids` is specified, the result set will be further limited to
    the specified ids."""
    db = request.db.sessions
    user = request.user.username if request.user.is_authenticated else None

    query = db.Select(sets='notifications', where='user IS NULL')
    if user:
        query.where |= 'user = :user'

    if notification_ids:
        query.where += db.sqlin('notification_id', notification_ids)

    db.query(query, user=user)
    return [Notification(**to_dict(row)) for row in db.results]
