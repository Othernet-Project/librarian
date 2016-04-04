from .facets.archive import FacetsArchive


def refill_facets(arg, supervisor):
    print('Begin facets refill.')
    config = supervisor.config
    archive = FacetsArchive(supervisor.exts.fsal,
                            supervisor.exts.databases.facets,
                            config=config)
    archive.clear_and_reload()
    print('Facet refill finished.')
    raise supervisor.EarlyExit()
