import sys

from .fsck import check_integrity


RECOVER = 'recover'
RECOVERY_IMPOSSIBLE = 'recovery_impossible'


def initialize(supervisor):
    supervisor.APP_HOOKS += (RECOVER, RECOVERY_IMPOSSIBLE)

    def recovery_failed():
        supervisor.events.publish(supervisor.IMMEDIATE_SHUTDOWN, supervisor)
        sys.exit(1)

    is_dirty = check_integrity(supervisor.config)
    if is_dirty:
        # If dirty flags are found, prepare for handling recovery failures
        # and fire the recover event
        supervisor.events.subscribe(RECOVERY_IMPOSSIBLE, recovery_failed)
        supervisor.events.publish(RECOVER, supervisor)
