import functools
import importlib

from fsal.client import FSAL
from ondd_ipc.ipc import ONDDClient

from .core.exts import ext_container as exts
from .data.notifications import Notification
from .data.settings import SettingsManager
from .data.setup import Setup, SetupWizard
from .helpers.notifications import invalidate_notification_cache
from .presentation.dashboard.registry import DashboardPluginRegistry
from .presentation.menu.registry import MenuItemRegistry
from .tasks.diskspace import check_diskspace
from .tasks.facets import check_new_content, scan_facets
from .tasks.filemanager import check_dirinfo
from .tasks.notifications import notification_cleanup
from .tasks.ondd import query_cache_storage_status


SCAN_DELAY = 5
STEP_DELAY = 0.5


def import_attr(path):
    separated = path.split('.')
    mod_path = '.'.join(separated[:-1])
    attr_name = separated[-1]
    mod = importlib.import_module(mod_path)
    return getattr(mod, attr_name)


def install_extensions(supervisor):
    exts.fsal = FSAL(exts.config['fsal.socket'])
    exts.dashboard = DashboardPluginRegistry()
    exts.menuitems = MenuItemRegistry()
    exts.notifications = Notification
    exts.notifications.on_send(invalidate_notification_cache)
    exts.ondd = ONDDClient(exts.config['ondd.socket'])
    exts.settings = SettingsManager(supervisor)
    exts.setup = Setup(supervisor)
    exts.setup_wizard = SetupWizard(name='setup')


def register_commands():
    for command_path in exts.config['command.handlers']:
        command_cls = import_attr(command_path)
        exts.commands.register(command_cls.name,
                               command_cls(),
                               command_cls.option,
                               command_cls.action,
                               command_cls.help)


def register_menu_items():
    for menuitem_path in exts.config['menu.items']:
        menuitem_cls = import_attr(menuitem_path)
        exts.menuitems.register(menuitem_cls)


def register_dashboard_plugins():
    for plugin_path in exts.config['dashboard.plugins']:
        plugin_cls = import_attr(plugin_path)
        exts.dashboard.register(plugin_cls)


def register_wizard_steps():
    for step_path in exts.config['setup.steps']:
        step_cls = import_attr(step_path)
        exts.setup_wizard.register_class(step_cls)


def register_settings():
    for field_path in exts.config['settings.fields']:
        field_cls = import_attr(field_path)
        field = field_cls()
        exts.settings.add_group(field.group, field.verbose_group)
        exts.settings.add_field(**field.rules)


def initialize(supervisor):
    install_extensions()
    register_commands()
    register_menu_items()
    register_dashboard_plugins()
    register_wizard_steps()
    register_settings()
    exts.events.subscribe('FS_EVENT',
                          functools.partial(check_dirinfo, supervisor))


def init_complete(supervisor):
    exts.dashboard.sort()
    exts.menuitems.sort(supervisor.config)


def schedule_diskspace_check(supervisor):
    check_diskspace(supervisor)
    refresh_rate = exts.config['diskspace.refresh_rate']
    if not refresh_rate:
        return
    exts.tasks.schedule(check_diskspace,
                        args=(supervisor,),
                        delay=refresh_rate,
                        periodic=True)


def schedule_facets_scan(supervisor):
    refresh_rate = exts.config['facets.refresh_rate']
    exts.tasks.schedule(check_new_content,
                        args=(supervisor, refresh_rate),
                        delay=refresh_rate)
    if exts.config.get('facets.scan', False):
        start_delay = exts.config.get('facets.scan_delay', SCAN_DELAY)
        step_delay = exts.config.get('facets.scan_step_delay', STEP_DELAY)
        kwargs = dict(step_delay=step_delay, config=exts.config)
        exts.tasks.schedule(scan_facets, kwargs=kwargs, delay=start_delay)


def schedule_notification_cleanup():
    # schedule notification cleanup task
    db = exts.databases.notifications
    default_expiry = exts.config['notifications.default_expiry']
    exts.tasks.schedule(notification_cleanup,
                        args=(db, default_expiry),
                        periodic=True,
                        delay=default_expiry)


def schedule_ondd_cache_check(supervisor):
    refresh_rate = exts.config['ondd.cache_refresh_rate']
    exts.tasks.schedule(query_cache_storage_status,
                        args=(supervisor,),
                        delay=refresh_rate,
                        periodic=True)


def post_start(supervisor):
    schedule_notification_cleanup()
    schedule_diskspace_check(supervisor)
    schedule_facets_scan(supervisor)
    schedule_ondd_cache_check(supervisor)
