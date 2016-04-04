import os

from .dirinfo import DirInfo


def is_dirinfo(event):
    if not event.is_dir:
        name = os.path.basename(event.src)
        return name == DirInfo.FILENAME
    return False


def delete_dirinfo(supervisor, path):
    entries = DirInfo.from_db(supervisor, [path])
    for dirinfo in entries.values():
        dirinfo.delete()


def check_dirinfo(supervisor, event):
    if not is_dirinfo(event):
        return
    dirname = os.path.dirname(event.src)
    if event.event_type == 'created':
        DirInfo.from_file(supervisor, dirname)
    elif event.event_type == 'modified':
        delete_dirinfo(supervisor, dirname)
        DirInfo.from_file(supervisor, dirname)
    elif event.event_type == 'deleted':
        delete_dirinfo(supervisor, dirname)
