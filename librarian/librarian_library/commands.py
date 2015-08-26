from .library.archive import Archive


def refill_db(supervisor):
    print('Begin content refill.')
    config = supervisor.config
    archive = Archive.setup(config['library.backend'],
                            supervisor.exts.databases.main,
                            unpackdir=config['content.unpackdir'],
                            contentdir=config['content.contentdir'],
                            spooldir=config['content.spooldir'],
                            meta_filename=config['content.metadata'])
    archive.clear_and_reload()
    print('Content refill finished.')
    raise supervisor.EarlyExit()


def reload_db(supervisor):
    print('Begin content reload.')
    config = supervisor.config
    archive = Archive.setup(config['library.backend'],
                            supervisor.exts.databases.main,
                            unpackdir=config['content.unpackdir'],
                            contentdir=config['content.contentdir'],
                            spooldir=config['content.spooldir'],
                            meta_filename=config['content.metadata'])
    archive.reload_content()
    print('Content reload finished.')
    raise supervisor.EarlyExit()
