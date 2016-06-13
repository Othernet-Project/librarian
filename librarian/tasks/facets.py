import logging

from fsal.events import EVENT_CREATED, EVENT_DELETED, EVENT_MODIFIED
from greentasks import Task

from ..core.exts import ext_container as exts
from ..data.meta.archive import Archive


class CheckNewContentTask(Task):
    REPEAT_DELAY = 3  # seconds
    INCREMENT_DELAY = 5  # surprisignly also seconds

    name = 'facets'
    periodic = True

    def __init__(self):
        self.changes_found = False
        self.archive = Archive()

    def get_start_delay(self):
        return exts.config['facets.refresh_rate']

    def get_delay(self, previous_delay):
        # if changes were found, reschedule asap as there is a possibility that
        # more changes are queued up by FSAL
        if self.changes_found:
            return self.REPEAT_DELAY
        max_delay = exts.config['facets.refresh_rate']
        if previous_delay is None:
            return max_delay
        # when no changes were found, start decreasing the frequency of checks
        # slowly, until it gets back to the originally specified value
        if previous_delay + self.INCREMENT_DELAY <= max_delay:
            return previous_delay + self.INCREMENT_DELAY
        # originally specified value reached
        return max_delay

    def run(self):
        analyzable = []
        removable = []
        for event in exts.fsal.get_changes():
            self.changes_found = True
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
            self.archive.remove(removable)
        if analyzable:
            self.archive.analyze(analyzable, callback=self.archive.save_many)
