from ...presentation.dashboard.registry import DashboardPluginRegistry
from ..exports import (ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector)


class DashboardPlugins(ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector):
    """
    This collector collects dashboard plugins.
    """
    export_key = 'dashboard'
    registry_class = DashboardPluginRegistry
    ext_name = 'dashboard'
