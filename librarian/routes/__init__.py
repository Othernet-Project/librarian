from bottle import error

from ..core.exts import ext_container as exts
from ..utils.filters import safepath_filter
from . import (auth, dashboard, diskspace, filemanager, lang, logs,
               notifications, ondd, settings, setup, system)


def routes(config):
    exts.bottle_app.router.add_filter('safepath', safepath_filter)
    error(403)(system.error_403)
    error(404)(system.error_404)
    error(500)(system.error_500)
    error(503)(system.error_503)
    auth.Login.route('/login/', app=exts.bottle_app)
    auth.Logout.route('/logout/', app=exts.bottle_app)
    auth.PasswordReset.route('/reset-password/', app=exts.bottle_app)
    auth.EmergencyReset.route('/emergency/', app=exts.bottle_app)
    dashboard.Dashboard.route(app=exts.bottle_app)
    diskspace.Consolidate.route(app=exts.bottle_app)
    diskspace.ConsolidateState.route(app=exts.bottle_app)
    filemanager.List.route('/files/<path:safepath>', app=exts.bottle_app)
    filemanager.Details.route('/details/<path:safepath>', app=exts.bottle_app)
    filemanager.Direct.route('/direct/<path:safepath>', app=exts.bottle_app)
    filemanager.Delete.route('/delete/<path:safepath>', app=exts.bottle_app)
    filemanager.Thumb.route('/thumb/<path:safepath>', app=exts.bottle_app)
    lang.List.route(app=exts.bottle_app)
    logs.SendAppLog.route(app=exts.bottle_app)
    logs.SendDiag.route(app=exts.bottle_app)
    notifications.List.route(app=exts.bottle_app)
    ondd.Status.route(app=exts.bottle_app)
    ondd.FileList.route(app=exts.bottle_app)
    ondd.CacheStatus.route(app=exts.bottle_app)
    ondd.Settings.route(app=exts.bottle_app)
    settings.Settings.route(app=exts.bottle_app)
    setup.Enter.route(app=exts.bottle_app)
    setup.Exit.route(app=exts.bottle_app)
    setup.Diag.route(app=exts.bottle_app)
    route_config = (
        # This route handler is added because unhandled missing pages cause
        # bottle to _not_ install any plugins, and some are essential to
        # rendering of the 404 page (e.g., i18n, sessions, auth).
        ('sys:all404', system.all_404,
         ['GET', 'POST'], '/<path:path>', dict()),
    )
    if config.get('app.default_route'):
        route_config = (
            ('sys:root', system.root_handler, 'GET', '/', dict()),
        ) + route_config
    return route_config
