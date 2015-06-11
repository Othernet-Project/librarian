"""
notifications.py: notifications menu item
Copyright 2014-2015, Outernet Inc.
Some rights reserved.
This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import MenuItem

from bottle_utils.i18n import lazy_gettext as _

from ..utils.notifications import get_notifications


class NotificationsMenuItem(MenuItem):
    icon_class = 'notifications'
    alt_icon_class = 'notifications unread'
    route = 'notifications:list'
    group = 'main'

    def __init__(self, *args, **kwargs):
        super(NotificationsMenuItem, self).__init__(*args, **kwargs)
        self.notifications = list(get_notifications())
        self.unread_count = len([notification
                                 for notification in self.notifications
                                 if not notification.is_read])

    def is_visible(self):
        return len(self.notifications) > 0

    def is_alt_icon_visible(self):
        return self.unread_count > 0

    @property
    def label(self):
        if self.unread_count > 0:
            return _("Notifications") + ' ({0})'.format(self.unread_count)

        return _("Notifications")
