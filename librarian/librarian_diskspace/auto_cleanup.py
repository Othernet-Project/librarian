import logging

from librarian.librarian_library.library.archive import Archive

from . import zipballs


def auto_cleanup(supervisor):
    (free, _) = zipballs.free_space(config=supervisor.config)
    needed_space = zipballs.needed_space(free, config=supervisor.config)
    if not needed_space:
        return

    archive = Archive.setup(
        supervisor.config['library.backend'],
        supervisor.exts.databases.main,
        unpackdir=supervisor.config['library.unpackdir'],
        contentdir=supervisor.config['library.contentdir'],
        spooldir=supervisor.config['library.spooldir'],
        meta_filename=supervisor.config['library.metadata']
    )
    deletable_list = zipballs.cleanup_list(free,
                                           db=supervisor.exts.databases.main,
                                           config=supervisor.config)
    content_ids = [content['md5'] for content in deletable_list]
    deleted = archive.remove_from_archive(content_ids)
    msg = "Automatic cleanup has deleted {0} content entries.".format(deleted)
    logging.info(msg)
