from os.path import basename

from bottle import error

from ..core.exts import ext_container as exts
from . import (auth, dashboard, diskspace, emergency_reset, filemanager, lang,
               logs, notifications, ondd, settings, setup, system)


def routes(config):
    skip_plugins = config['app.skip_plugins']
    error(403)(system.error_403)
    error(404)(system.error_404)
    error(500)(system.error_500)
    error(503)(system.error_503)
    auth.Login.route('/login/', app=exts.bottle_app)
    auth.Logout.route('/logout/', app=exts.bottle_app)
    auth.ResetPassword.route('/reset-password/', app=exts.bottle_app)
    route_config = (
        ('emergency:reset_form', emergency_reset.show_emergency_reset_form,
         'GET', '/emergency/', {'skip': ['sessions']}),
        ('emergency:reset', emergency_reset.reset,
         'POST', '/emergency/', {'skip': ['sessions']}),
        ('dashboard:main', dashboard.dashboard,
         'GET', '/dashboard/', {}),
        ('diskspace:show_consolidate_form', diskspace.show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', diskspace.schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate_state', diskspace.consolidate_state,
         'GET', '/diskspace/consolidate/state', {}),
        ('files:list', filemanager.init_file_action,
         'GET', '/files/', dict(unlocked=True)),
        ('files:path', filemanager.init_file_action,
         'GET', '/files/<path:path>', dict(unlocked=True)),
        ('files:action', filemanager.handle_file_action,
         'POST', '/files/<path:path>', dict(unlocked=True)),
        ('files:direct', filemanager.direct_file,
         'GET', '/direct/<path:path>', dict(unlocked=True)),
        ('ui:lang_list', lang.lang_list,
         'GET', '/languages/', {}),
        ('sys:applog', logs.send_applog,
         'GET', '/' + basename(config['logging.output']), dict(unlocked=True)),
        ('sys:syslog', logs.send_diags,
         'GET', '/syslog', dict(unlocked=True)),
        ('notifications:list', notifications.notification_list,
         'GET', '/notifications/', {}),
        ('notifications:read', notifications.notifications_read,
         'POST', '/notifications/', {}),
        ('ondd:status', ondd.get_signal_status,
         'GET', '/ondd/status/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:files', ondd.show_file_list,
         'GET', '/ondd/files/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:cache_status', ondd.show_cache_status,
         'GET', '/ondd/cache/', dict(unlocked=True, skip=skip_plugins)),
        ('ondd:settings', ondd.show_settings_form,
         'GET', '/ondd/settings/', dict(unlocked=True)),
        ('ondd:settings', ondd.set_settings,
         'POST', '/ondd/settings/', dict(unlocked=True)),
        ('settings:load', settings.show_settings_form,
         'GET', '/settings/', dict(unlocked=True)),
        ('settings:save', settings.save_settings,
         'POST', '/settings/', dict(unlocked=True)),
        ('setup:main', setup.enter_wizard,
         ['GET', 'POST'], '/setup/', {}),
        ('setup:exit', setup.exit_wizard,
         'GET', '/setup/exit/', {}),
        ('setup:diag', setup.diag,
         'GET', '/diag/', {}),
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
