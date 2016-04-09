import logging

from ..exports import DependencyCollector


class Plugins(DependencyCollector):
    """
    This collector collects Bottle plugins.
    """
    def collect(self, component):
        plugins = component.get_export('plugins', [])
        for p in plugins:
            try:
                plugin = component.get_object(p)
            except ImportError:
                logging.exception('Failed to import plugin {}'.format(p))
                continue
            self.register(plugin)

    def install_member(self, plugin):
        self.supervisor.app.install(plugin)
