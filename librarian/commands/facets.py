from ..core.exceptions import EarlyExit
from ..core.exts import ext_container as exts
from ..data.meta.archive import Archive


class RefillFacetsCommand(object):
    name = 'refill_facets'
    flags = '--refill-facets'
    kwargs = {
        'action': 'store_true',
        'help': "Empty facets archive and reconstruct it."
    }

    def run(self, args):
        if not args.refill_facets:
            return

        print('Begin facets refill.')
        archive = Archive(fsal=exts.fsal,
                          db=exts.databases.meta,
                          tasks=exts.tasks,
                          config=exts.config)
        archive.clear_and_reload()
        print('Facet refill finished.')
        raise EarlyExit()
