import functools
import logging
import os
import collections

from fsal.events import EVENT_CREATED, EVENT_DELETED, EVENT_MODIFIED

from librarian_core.exts import ext_container as exts

from .facets.utils import get_archive


REPEAT_DELAY = 3  # seconds
INCREMENT_DELAY = 5  # surprisignly also seconds


def is_content(event, meta_filenames):
    if not event.is_dir:
        filename = os.path.basename(event.src)
        return filename in meta_filenames
    return False


def reschedule_content_check(fn):
    @functools.wraps(fn)
    def wrapper(supervisor, current_delay):
        changes_found = False
        try:
            changes_found = fn(supervisor)
        finally:
            if changes_found:
                refresh_rate = REPEAT_DELAY
            else:
                max_delay = supervisor.config['facets.refresh_rate']
                if current_delay + INCREMENT_DELAY <= max_delay:
                    refresh_rate = current_delay + INCREMENT_DELAY
                else:
                    refresh_rate = max_delay

            supervisor.exts.tasks.schedule(check_new_content,
                                           args=(supervisor, refresh_rate),
                                           delay=refresh_rate)
    return wrapper


@reschedule_content_check
def check_new_content(supervisor):
    config = supervisor.config
    facets_archive = get_archive(db=supervisor.exts.databases.facets,
                                 config=config)
    changes_found = False
    for event in supervisor.exts.fsal.get_changes():
        changes_found = True
        fpath = event.src
        is_file = not event.is_dir
        if is_file and event.event_type in (EVENT_CREATED, EVENT_MODIFIED):
            logging.info(u"Update file facets: '{}'".format(fpath))
            facets_archive.update_facets(fpath)
        elif is_file and event.event_type == EVENT_DELETED:
            logging.info(u"Removing file facets: '{}'".format(fpath))
            facets_archive.remove_facets(fpath)
        supervisor.exts.events.publish('FS_EVENT', event)
    return changes_found


def scan_facets(path_queue=None, step_delay=0, config=None):
    if path_queue is None:
        path_queue = collections.deque()
        path_queue.append('.')
    if not path_queue:
        logging.info(u'Facets scan complete.')
        return

    dir_path = path_queue.popleft()
    logging.debug(u'Scanning facets for files in {}'.format(dir_path))
    success, dirs, files = exts.fsal.list_dir(dir_path)
    if not success:
        logging.warn(
            u'Facets scan for {} stopped. Invalid path.'.format(dir_path))
        return

    archive = get_archive(config=config)
    for f in files:
        if not archive.get_facets(f.rel_path):
            logging.info(u"Update file facets: '{}'".format(f.rel_path))
            archive.update_facets(f.rel_path)
    path_queue.extend((d.rel_path for d in dirs))

    kwargs = dict(path_queue=path_queue, step_delay=step_delay,
                  config=config)
    exts.tasks.schedule(scan_facets, kwargs=kwargs)
