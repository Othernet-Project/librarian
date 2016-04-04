"""
notifications.py: Notification system

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime
import functools
import json
import uuid

from bottle import request
from bottle_utils.common import basestring, unicode

from librarian_core.utils import utcnow


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
    'groupable',
    'username',
)


TARGET_COLS = (
    'target_id',
    'notification_id',
    'target_type',
    'target'
)


def to_dict(row):
    return dict((key, row[key]) for key in row.keys())


class Notification(object):
    NORMAL = 0
    URGENT = 1
    CRITICAL = 2
    PRIORITIES = (NORMAL, URGENT, CRITICAL)
    VERBOSE_PRIORITIES = {
        NORMAL: 'normal',
        URGENT: 'urgent',
        CRITICAL: 'critical',
    }
    on_send_callbacks = []

    def __init__(self, notification_id, message, created_at, category=None,
                 icon=None, priority=NORMAL, expires_at=None, dismissable=True,
                 groupable=True, read_at=None, username=None, db=None):
        self.notification_id = notification_id
        try:
            self.message = json.loads(message)
        except ValueError:
            self.message = unicode(message)

        self.created_at = created_at
        self.category = category
        self.icon = icon
        self.priority = priority
        self.expires_at = expires_at
        self.dismissable = dismissable
        self.groupable = groupable
        self._read_at = read_at
        self.username = username
        self.db = db or request.db.notifications

    @property
    def verbose_priority(self):
        return self.VERBOSE_PRIORITIES[self.priority]

    @classmethod
    def on_send(cls, callback):
        cls.on_send_callbacks.append(callback)

    @classmethod
    def send(cls, message, category=None, icon=None, priority=NORMAL,
             expiration=0, dismissable=True, groupable=True, username=None,
             group=None, db=None):
        """ Creates a notification and a notification target

        Short description of variables:
            message:        text of the notification (may be json)
            category:       category of the notification
            icon:           unimplemented
            priority:       unimplemented
            dismissable:    whether the notification can be dismissed
            groupable:      whether notifications may be stacked
            username:       username target should be created for
            group:          group name to target - special group "guest" for
                            anonymous users

        Notification targetting:
            Targets are created for the notification once. First option is
            username, second is group, and if none are provided, special group
            "all" is used.
        """
        if not isinstance(message, basestring):
            message = json.dumps(message)
        notification_id = cls.generate_unique_id()
        instance = cls(notification_id=notification_id,
                       message=message,
                       created_at=utcnow(),
                       category=category,
                       icon=icon,
                       priority=priority,
                       expires_at=cls.calc_expiry(expiration),
                       dismissable=dismissable,
                       groupable=groupable,
                       read_at=None,
                       username=username,
                       db=db)
        instance.save()
        NotificationTarget.create(
            notification_id,
            target=username or group or 'all',
            target_type='user' if username else 'group',
            db=db,
        )
        # when notification is sent, invoke subscribers of on_send with
        # notification instance as their only argument
        for callback in cls.on_send_callbacks:
            callback(instance)

        return instance

    @property
    def has_expired(self):
        return self.expires_at is not None and self.expires_at < utcnow()

    @property
    def is_shared(self):
        return not self.username

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
        notifications = request.user.options.get('notifications', {})
        notifications[self.notification_id] = read_at
        request.user.options['notifications'] = notifications

    def _mark_private_read(self, read_at):
        query = self.db.Update('notifications',
                               read_at='%(read_at)s',
                               where='notification_id = %(notification_id)s')
        self.db.execute(query, dict(notification_id=self.notification_id,
                                    read_at=read_at))
        self._read_at = read_at

    def mark_read(self, read_at=None):
        read_at = utcnow() if read_at is None else read_at
        if not self.is_read:
            if self.is_shared:
                # shared notifications store the datetime of reading in the
                # user's session
                self._mark_shared_read(read_at)
            else:
                # only personal notifications can be marked as read in the db
                self._mark_private_read(read_at)

        return self

    def safe_message(self, *key_chain):
        """Attempt retrieveng the value under the passed in keys if message is
        a JSON object, otherwise just return the message itself."""
        if isinstance(self.message, basestring):
            return self.message

        return functools.reduce(lambda src, key: src[key],
                                key_chain,
                                self.message)

    def save(self):
        query = self.db.Replace('notifications',
                                constraints=['notification_id'],
                                cols=NOTIFICATION_COLS)
        # allow both arbitary strings as well as json objects as notification
        # message
        if isinstance(self.message, basestring):
            message = self.message
        else:
            message = json.dumps(self.message)

        self.db.execute(query, dict(notification_id=self.notification_id,
                                    message=message,
                                    created_at=self.created_at,
                                    category=self.category,
                                    icon=self.icon,
                                    priority=self.priority,
                                    expires_at=self.expires_at,
                                    dismissable=self.dismissable,
                                    groupable=self.groupable,
                                    read_at=self._read_at,
                                    username=self.username))
        return self

    def delete(self):
        target_query = self.db.Delete('notification_targets',
                                      where='notification_id = %s')
        query = self.db.Delete('notifications', where='notification_id = %s')
        self.db.execute(target_query, (self.notification_id,))
        self.db.execute(query, (self.notification_id,))
        return self

    @staticmethod
    def generate_unique_id():
        return uuid.uuid4().hex

    @staticmethod
    def calc_expiry(expiration):
        if expiration == 0:
            return None

        return utcnow() + datetime.timedelta(seconds=expiration)

    @classmethod
    def delete_by_category(cls, category, db):
        query = db.Delete('notifications',
                          where='notifications.category = %s')
        where = ('notifications.category = %s AND '
                 'notification_targets.notification_id = '
                 'notifications.notification_id')
        target_query = db.Delete('notification_targets USING notifications',
                                 where=where)
        db.execute(target_query, [category])
        db.execute(query, [category])


class NotificationTarget(object):

    def __init__(self, target_id, notification_id, target,
                 target_type='group', db=None):
        self.target_id = target_id
        self.target = target
        self.target_type = target_type
        self.notification_id = notification_id
        self.db = db or request.db.notifications

    @classmethod
    def create(cls, notification_id, target, target_type='group', db=None):
        instance = cls(target_id=cls.generate_unique_id(),
                       notification_id=notification_id,
                       target=target,
                       target_type=target_type,
                       db=db)
        instance.save()
        return instance

    def save(self):
        query = self.db.Replace('notification_targets',
                                constraints=['target_id'],
                                cols=TARGET_COLS)
        self.db.execute(query, dict(target_id=self.target_id,
                                    notification_id=self.notification_id,
                                    target=self.target,
                                    target_type=self.target_type))
        return self

    def delete(self):
        query = self.db.Delete('notification_targets', where='target_id = %s')
        self.db.execute(query, (self.target_id,))
        return self

    @staticmethod
    def generate_unique_id():
        return uuid.uuid4().hex


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
        'verbose_priority',
    )
    # columns that require a value other than NULL in order to pass the check
    # for similarity
    value_required = (
        'category',
    )

    def __init__(self, notifications=None):
        self.notifications = notifications or []

    def __getattr__(self, name):
        if name in self.proxied_attrs:
            try:
                return getattr(self.notifications[-1], name)
            except IndexError:
                raise ValueError('Notification group has 0 notifications.')

        cls_name = self.__class__.__name__
        msg = "'{0}' object has no attribute '{1}'".format(cls_name, name)
        raise AttributeError(msg)

    @property
    def first_id(self):
        """Returns the ``notification_id`` of the very first notification in
        the group."""
        try:
            return getattr(self.notifications[0], 'notification_id')
        except IndexError:
            raise ValueError('Notification group has 0 notifications.')

    def add(self, notification):
        self.notifications.append(notification)

    @property
    def count(self):
        return len(self.notifications)

    def is_similar(self, notification, attrs):
        """Returns whether `notification` is similar to existing members of the
        group or not."""
        def are_equal(name):
            value = getattr(self, name)
            other = getattr(notification, name)
            is_value_required = name in self.value_required
            return (value or not is_value_required) and value == other

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
                if (not notification.groupable or
                        not group.is_similar(notification, attrs=by)):
                    group = cls()
                    group_list.append(group)

                group.add(notification)

            return group_list
