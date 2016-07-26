from ..core.exceptions import EarlyExit
from ..core.exts import ext_container as exts
from ..data.meta.archive import Archive


class ReloadMetaCommand(object):
    name = 'reload_meta'
    flags = '--reload-meta'
    kwargs = {
        'action': 'store_true',
        'help': "Empty meta archive and reconstruct it."
    }

    def run(self, args):
        exts.events.subscribe('init_complete', self.reload)

    def reload(self, *args, **kwargs):
        print('Begin meta reload.')
        archive = Archive(fsal=exts.fsal,
                          db=exts.databases.librarian,
                          tasks=exts.tasks,
                          config=exts.config)
        archive.clear_and_reload()
        print('Meta reload finished.')
        raise EarlyExit()
