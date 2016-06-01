from ..data.facets.archive import FacetsArchive


class RefillFacetsCommand(object):
    name = 'refill_facets'
    flags = '--refill-facets'
    kwargs = {
        'action': 'store_true',
        'help': "Empty facets archive and reconstruct it."
    }

    def __call__(self, arg, supervisor):
        print('Begin facets refill.')
        config = supervisor.config
        archive = FacetsArchive(supervisor.exts.fsal,
                                supervisor.exts.databases.facets,
                                config=config)
        archive.clear_and_reload()
        print('Facet refill finished.')
        raise supervisor.EarlyExit()
