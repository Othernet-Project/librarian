import functools
import logging

from fsal.events import EVENT_CREATED, EVENT_DELETED, EVENT_MODIFIED

from ..core.exts import ext_container as exts
from ..data.facets.archive import Archive
from . import Task


REPEAT_DELAY = 3  # seconds
INCREMENT_DELAY = 5  # surprisignly also seconds
SCAN_DELAY = 5
STEP_DELAY = 0.5


class CheckNewContentTask(Task):

    def reschedule_content_check(fn):
        @functools.wraps(fn)
        def wrapper(self, current_delay):
            changes_found = False
            try:
                changes_found = fn(self)
            finally:
                if changes_found:
                    refresh_rate = REPEAT_DELAY
                else:
                    max_delay = exts.config['facets.refresh_rate']
                    if current_delay + INCREMENT_DELAY <= max_delay:
                        refresh_rate = current_delay + INCREMENT_DELAY
                    else:
                        refresh_rate = max_delay

                exts.tasks.schedule(self,
                                    args=(refresh_rate,),
                                    delay=refresh_rate)
        return wrapper

    @reschedule_content_check
    def run(self):
        archive = Archive()
        changes_found = False
        analyzable = []
        removable = []
        for event in exts.fsal.get_changes():
            changes_found = True
            path = event.src
            is_file = not event.is_dir
            if is_file and event.event_type in (EVENT_CREATED, EVENT_MODIFIED):
                logging.info(u"Update file facets: '{}'".format(path))
                analyzable.append(path)
            elif is_file and event.event_type == EVENT_DELETED:
                logging.info(u"Removing file facets: '{}'".format(path))
                removable.append(path)
            exts.events.publish('FS_EVENT', event)
        if removable:
            archive.remove(removable)
        if analyzable:
            archive.analyze(analyzable)
        return changes_found

    @classmethod
    def install(cls):
        refresh_rate = exts.config['facets.refresh_rate']
        exts.tasks.schedule(cls(),
                            args=(refresh_rate,),
                            delay=refresh_rate)


class ScanFacetsTask(Task):

    def run(self, step_delay=0):
        archive = Archive()
        archive.scan(callback=archive.save_many, delay=step_delay)

    @classmethod
    def install(cls):
        if exts.config.get('facets.scan', False):
            start_delay = exts.config.get('facets.scan_delay', SCAN_DELAY)
            step_delay = exts.config.get('facets.scan_step_delay', STEP_DELAY)
            exts.tasks.schedule(cls(),
                                kwargs=dict(step_delay=step_delay),
                                delay=start_delay)
