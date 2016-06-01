from ..data.meta.archive import Archive


class RefillFacetsCommand(object):
    name = 'refill_facets'
    flags = '--refill-facets'
    kwargs = {
        'action': 'store_true',
        'help': "Empty facets archive and reconstruct it."
    }

    def run(self, arg, supervisor):
        print('Begin facets refill.')
        config = supervisor.config
        archive = Archive(fsal=supervisor.exts.fsal,
                          db=supervisor.exts.databases.meta,
                          tasks=supervisor.exts.tasks,
                          config=config)
        archive.clear_and_reload()
        print('Facet refill finished.')
        raise supervisor.EarlyExit()
