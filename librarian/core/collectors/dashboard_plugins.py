from ..exports import ObjectCollectorMixin, ListCollector
from ..presentation.dashboard.registry import DashboardPluginRegistry


class DashboardPlugins(ObjectCollectorMixin, ListCollector):
    """
    This collector collects dashboard plugins.
    """
    export_key = 'dashboard'

    def __init__(self, supervisor):
        super(DashboardPlugins, self).__init__(supervisor)
        self.plugins = self.supervisor.exts = DashboardPluginRegistry()

    def install_member(self, plugin):
        self.plugins.register(plugin)
