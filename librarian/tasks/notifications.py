import datetime
import logging

from ..core.exts import ext_container as exts
from ..core.utils import utcnow
from . import Task


class NotificationCleanupTask(Task):

    def run(self, db, default_expiry):
        logging.debug("Notification cleanup started.")
        now = utcnow()
        auto_expires_at = now - datetime.timedelta(seconds=default_expiry)
        where = '''notifications.dismissable = true AND (
                    (notifications.expires_at IS NULL AND
                     notifications.created_at <= %(auto_expires_at)s) OR
                     notifications.expires_at <= %(now)s)'''
        query = db.Delete('notifications', where=where)
        target_query = db.Delete('notification_targets USING notifications',
                                 where=where)
        target_query.where += ('notification_targets.notification_id = '
                               'notifications.notification_id')
        params = dict(now=now, auto_expires_at=auto_expires_at)
        db.execute(target_query, params)
        rows = db.execute(query, params)
        logging.debug("{} expired notifications deleted.".format(rows))

    @classmethod
    def install(cls):
        instance = cls()
        db = exts.databases.notifications
        default_expiry = exts.config['notifications.default_expiry']
        exts.tasks.schedule(instance,
                            args=(db, default_expiry),
                            periodic=True,
                            delay=default_expiry)
