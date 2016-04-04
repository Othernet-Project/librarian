from .menuitems import DashboardMenuItem
from .registry import DashboardPluginRegistry


def initialize(supervisor):
    supervisor.exts.dashboard = DashboardPluginRegistry()
    supervisor.exts.menuitems.register(DashboardMenuItem)


def init_complete(supervisor):
    supervisor.exts.dashboard.sort()
