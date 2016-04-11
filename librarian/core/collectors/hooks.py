import logging

from ..exports import ObjectCollectorMixin, ListCollector


class Hooks(ObjectCollectorMixin, ListCollector):
    """
    This class collects event hooks that should be installed during supervisor
    start-up.
    """
    export_key = 'hooks'

    def install_member(self, hook):
        hook_name = getattr(hook, 'hook', None)
        if not hook_name:
            logging.error('Missing hook name for {}'.format(hook))
            return
        self.events.subscribe(hook_name, hook)
