import logging

from ..exports import ListCollector


class Hooks(ListCollector):
    """
    This class collects event hooks that should be installed during supervisor
    start-up.
    """
    def collect(self, component):
        hooks = component.get_export('hooks', [])
        for h in hooks:
            try:
                hook = component.get_object(h)
            except ImportError:
                logging.exception('Failed to import hook {}'.format(h))
                continue
            hook.component = component.name
            self.register(hook)

    def install_member(self, hook):
        hook_name = getattr(hook, 'hook', None)
        if not hook_name:
            logging.error('Missing hook name for {}'.format(hook))
            return
        self.events.subscribe(hook_name, hook)
