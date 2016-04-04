from .dashboard_plugin import LogsDashboardPlugin


def initialize(supervisor):
    supervisor.exts.dashboard.register(LogsDashboardPlugin)
