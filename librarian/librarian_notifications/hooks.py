from .notifications import Notification


def init_begin(supervisor):
    supervisor.exts.notifications = Notification
