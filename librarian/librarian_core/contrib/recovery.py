import os
import sys


def init_begin(supervisor):

    def recovery_failed():
        supervisor.events.publish(supervisor.IMMEDIATE_SHUTDOWN, supervisor)
        sys.exit(1)

    is_dirty = bool(os.listdir(supervisor.config['recovery.dirtydir']))
    if is_dirty:
        # If dirty flags are found, prepare for handling recovery failures
        # and fire the recover event
        supervisor.events.subscribe('RECOVERY_IMPOSSIBLE', recovery_failed)
        supervisor.events.publish('RECOVER', supervisor)
