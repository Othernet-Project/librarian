"""
notifications.py: routes related to notifications

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request
from bottle_utils.ajax import roca_view

from librarian_core.contrib.templates.renderer import template
from librarian_core.utils import utcnow

from .helpers import get_notifications, get_notification_groups
from .notifications import NotificationGroup


@roca_view('notification_list', '_notification_list', template_func=template)
def notification_list():
    return dict(groups=get_notification_groups())


def mark_read(notifications):
    now = utcnow()
    for notification in notifications:
        if notification.dismissable:
            notification.mark_read(now)


@roca_view('notification_list', '_notification_list', template_func=template)
def notifications_read():
    read_all = request.forms.get('action') == 'mark_read_all'
    first_notification_id = request.forms.get('notification_id')
    groups = NotificationGroup.group_by(get_notifications(),
                                        by=('category', 'read_at'))
    for group in groups:
        if read_all:
            # all groups should be marked as read
            mark_read(group.notifications)
        elif group.first_id == first_notification_id:
            # match groups using the id of the first notification object, so
            # even if new notifications are added to the group since the last
            # fetch by the client, it will still be able to find the correct
            # group.
            mark_read(group.notifications)
            break

    for key_tmpl in ('notification_group_{0}', 'notification_count_{0}'):
        key = key_tmpl.format(request.session.id)
        request.app.supervisor.exts.cache.delete(key)

    return dict(groups=[grp for grp in groups if not grp.is_read])


def routes(app):
    return (
        ('notifications:list', notification_list,
         'GET', '/notifications/', {}),
        ('notifications:read', notifications_read,
         'POST', '/notifications/', {}),
    )
