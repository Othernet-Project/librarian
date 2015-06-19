"""
notifications.py: routes related to notifications

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import datetime

from bottle import request
from bottle_utils.ajax import roca_view

from ..utils.notifications import get_notifications, NotificationGroup
from ..utils.template import template


@roca_view('notification_list', '_notification_list', template_func=template)
def notification_list():
    notifications = get_notifications()
    groups = NotificationGroup.group_by(notifications,
                                        by=('category', 'read_at'))
    return dict(groups=groups)


@roca_view('notification_list', '_notification_list', template_func=template)
def notifications_read():
    notification_ids = request.forms.getall('mark_read')
    notifications = get_notifications(notification_ids)
    read_at = datetime.datetime.now()
    for notification in notifications:
        if notification.dismissable:
            notification.mark_read(read_at)

    groups = NotificationGroup.group_by(get_notifications(),
                                        by=('category', 'read_at'))
    return dict(groups=groups)


def routes(app):
    return (
        ('notifications:list', notification_list,
         'GET', '/notifications/', {}),
        ('notifications:read', notifications_read,
         'POST', '/notifications/', {}),
    )
