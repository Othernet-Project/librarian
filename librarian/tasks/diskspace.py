from librarian_core.exts import ext_container as exts

from . import storage

# FIXME: The notifications messages need to be translatable

_ = lambda x: x


def clear_storage_notifications():
    db = exts.databases.notifications
    exts.notifications.delete_by_category('diskspace', db)


def send_storage_notification():
    db = exts.databases.notifications
    exts.notifications.send(
        _('Storage space is getting low. Please ask the administrator to take '
          'action.'),
        category='diskspace',
        dismissable=False,
        priority=exts.notifications.URGENT,
        group='guest',
        db=db)
    exts.notifications.send(
        _('Storage space is getting low. You will stop receiving new content '
          'if you run out of storage space. Please change or attach an '
          'external storage device.'),
        category='diskspace',
        dismissable=False,
        priority=exts.notifications.URGENT,
        group='superuser',
        db=db)


def check_diskspace(supervisor):
    config = supervisor.config
    threshold = config['diskspace.threshold']
    clear_storage_notifications()
    storage_devices = storage.get_content_storages()
    if not storage_devices:
        # None found, probably due to misconfiguration
        return
    # Note that we only check the last storage. It is assumed that the storage
    # configuration places external storage at the last position in the list.
    if int(storage_devices[-1].dev.stat.free) < threshold:
        send_storage_notification()
