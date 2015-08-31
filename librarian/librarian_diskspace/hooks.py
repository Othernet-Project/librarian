from .auto_cleanup import auto_cleanup


def initialize(supervisor):
    if supervisor.config.get('storage.auto_cleanup', False):
        supervisor.events.subscribe('background', auto_cleanup)
