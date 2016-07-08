from fsal.client import FSAL
from ondd_ipc.ipc import ONDDClient

from .core.exports import hook
from .core.exts import ext_container as exts
from .data.notifications import Notification
from .helpers.notifications import invalidate_notification_cache

from .routes import system
from .utils.filters import safepath_filter


@hook('initialize')
def initialize(supervisor):
    # add special url filter that performs unquoting automatically
    supervisor.app.router.add_filter('safepath', safepath_filter)
    # install extensions
    exts.fsal = FSAL(exts.config['fsal.socket'])
    exts.notifications = Notification
    exts.notifications.on_send(invalidate_notification_cache)
    exts.ondd = ONDDClient(exts.config['ondd.socket'])
    # register error handler routes
    supervisor.app.error(403)(system.error_403)
    supervisor.app.error(404)(system.error_404)
    supervisor.app.error(500)(system.error_500)
    supervisor.app.error(503)(system.error_503)


@hook('init_complete')
def init_complete(supervisor):
    exts.dashboard.sort()
    exts.menu.sort(supervisor.config)
