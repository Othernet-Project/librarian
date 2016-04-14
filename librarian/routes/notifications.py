"""
notifications.py: routes related to notifications

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from streamline import XHRPartialFormRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..core.utils import utcnow
from ..data.notifications import NotificationGroup
from ..forms.notifications import NotificationForm
from ..helpers.notifications import get_notifications, get_notification_groups


class List(XHRPartialFormRoute):
    path = '/notifications/'
    template_func = template
    template_name = 'notifications/notification_list'
    partial_template_name = 'notifications/_notification_list'
    form_factory = NotificationForm

    def show_form(self):
        return dict(groups=get_notification_groups())

    def mark_read(self, notifications):
        now = utcnow()
        for notification in notifications:
            if notification.dismissable:
                notification.mark_read(now)

    def invalidate_cache(self):
        for key_tmpl in ('notification_group_{}', 'notification_count_{}'):
            key = key_tmpl.format(self.request.session.id)
            exts.cache.delete(key)

    def form_valid(self):
        first_id = self.form.processed_data['notification_id']
        groups = NotificationGroup.group_by(get_notifications(),
                                            by=('category', 'read_at'))
        if not self.form.should_mark_all():
            # limit the list of groups to match only the one which needs to
            # be marked as read. matching is done by using the id of the first
            # notification object from the group, so even if new notifications
            # are added to the group since the last fetch by the client, it
            # will still be able to find the correct group.
            groups = [grp for grp in groups if grp.first_id == first_id]
        # loop through the groups and mark them as read
        for group in groups:
            self.mark_read(group.notifications)
        # invalidate cached notifications under current session, since their
        # state has changed now
        self.invalidate_cache()
        # return remaining unread notifications
        return dict(groups=[grp for grp in groups if not grp.is_read])
