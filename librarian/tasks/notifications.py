import datetime
import logging

from librarian_core.utils import utcnow


def notification_cleanup(db, default_expiry):
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
    db.execute(target_query, dict(now=now, auto_expires_at=auto_expires_at))
    rows = db.execute(query, dict(now=now, auto_expires_at=auto_expires_at))
    logging.debug("{} expired notifications deleted.".format(rows))
