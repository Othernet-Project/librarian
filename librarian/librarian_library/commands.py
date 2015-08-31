from .library.archive import Archive


def refill_db(arg, supervisor):
    print('Begin content refill.')
    config = supervisor.config
    archive = Archive.setup(config['library.backend'],
                            supervisor.exts.databases.main,
                            unpackdir=config['library.unpackdir'],
                            contentdir=config['library.contentdir'],
                            spooldir=config['library.spooldir'],
                            meta_filename=config['library.metadata'])
    archive.clear_and_reload()
    print('Content refill finished.')
    raise supervisor.EarlyExit()


def reload_db(arg, supervisor):
    print('Begin content reload.')
    config = supervisor.config
    archive = Archive.setup(config['library.backend'],
                            supervisor.exts.databases.main,
                            unpackdir=config['library.unpackdir'],
                            contentdir=config['library.contentdir'],
                            spooldir=config['library.spooldir'],
                            meta_filename=config['library.metadata'])
    archive.reload_content()
    print('Content reload finished.')
    raise supervisor.EarlyExit()
