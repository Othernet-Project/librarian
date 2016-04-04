from .notifications import Notification
from .tasks import notification_cleanup


def initialize(supervisor):
    supervisor.exts.notifications = Notification

    def invalidate_notification_cache(notification):
        # for now jsut invalidate the whole cache, no matter if it's a
        # private notification
        for key in ('notification_group', 'notification_count'):
            supervisor.exts.cache.invalidate(key)

    Notification.on_send(invalidate_notification_cache)


def init_complete(supervisor):
    # schedule notification cleanup task
    db = supervisor.exts.databases.notifications
    default_expiry = supervisor.config['notifications.default_expiry']
    supervisor.exts.tasks.schedule(notification_cleanup,
                                   args=(db, default_expiry),
                                   periodic=True,
                                   delay=default_expiry)
