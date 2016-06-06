import logging

from ..exports import ObjectCollectorMixin, ListCollector


#: Event name used to signal members to perform one-time initialization
INITIALIZE = 'initialize'


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
        # Initialize hook must be executed in-place, as soon as the component
        # loads. Currently it's hard-wired here, because anywhere else seemed
        # already too late to fire it, though a better alternative is welcome.
        if hook_name == INITIALIZE:
            hook(self.supervisor)
        else:
            self.events.subscribe(hook_name, hook)
