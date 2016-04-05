import os

from ..core.exts import ext_container as exts
from ..data.dirinfo import DirInfo
from . import Task


class CheckDirInfoTask(Task):

    def is_dirinfo(self, event):
        if not event.is_dir:
            name = os.path.basename(event.src)
            return name == DirInfo.FILENAME
        return False

    def delete_dirinfo(self, path):
        entries = DirInfo.from_db([path])
        for dirinfo in entries.values():
            dirinfo.delete()

    def check_dirinfo(self, event):
        if not self.is_dirinfo(event):
            return
        dirname = os.path.dirname(event.src)
        if event.event_type == 'created':
            DirInfo.from_file(dirname)
        elif event.event_type == 'modified':
            self.delete_dirinfo(dirname)
            DirInfo.from_file(dirname)
        elif event.event_type == 'deleted':
            self.delete_dirinfo(dirname)

    @classmethod
    def install(cls):
        exts.events.subscribe('FS_EVENT', cls())
