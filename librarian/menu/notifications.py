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
    alt_icon_class = 'notifications-active'
    route = 'notifications:list'

    def __init__(self, *args, **kwargs):
        super(NotificationsMenuItem, self).__init__(*args, **kwargs)
        self.notifications = list(get_notifications())
        self.unread_count = len([notification
                                 for notification in self.notifications
                                 if not notification.is_read])

    def is_alt_icon_visible(self):
        return self.unread_count

    @property
    def label(self):
        unread_count = self.unread_count
        if unread_count > 99:
            unread_count = '!'
        lbl = '<span class="notifications-label">{}</span>'.format(
            _("Notifications"))
        if unread_count > 0:
            lbl += ' <span class="count">{0}</span>'.format(unread_count)
        return lbl
