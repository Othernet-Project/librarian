from .dashboard_plugin import DiskspaceDashboardPlugin
from .tasks import check_diskspace


def initialize(supervisor):
    supervisor.exts.dashboard.register(DiskspaceDashboardPlugin)


def post_start(supervisor):
    check_diskspace(supervisor)
    refresh_rate = supervisor.config['diskspace.refresh_rate']
    if not refresh_rate:
        return
    supervisor.exts.tasks.schedule(check_diskspace,
                                   args=(supervisor,),
                                   delay=refresh_rate,
                                   periodic=True)
