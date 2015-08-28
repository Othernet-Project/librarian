from .notifications import Notification


def initialize(supervisor):
    supervisor.exts.notifications = Notification
