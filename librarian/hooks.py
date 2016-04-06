import importlib
import logging

from fsal.client import FSAL
from ondd_ipc.ipc import ONDDClient

from .core.exts import ext_container as exts
from .data.notifications import Notification
from .data.setup import Setup, SetupWizard
from .helpers.notifications import invalidate_notification_cache
from .presentation.dashboard.registry import DashboardPluginRegistry
from .presentation.menu.registry import MenuItemRegistry
from .presentation.settings import SettingsManager


def import_attr(path):
    separated = path.split('.')
    mod_path = '.'.join(separated[:-1])
    attr_name = separated[-1]
    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        logging.error('Failed to import {}'.format(mod_path))
        raise
    else:
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
                               action=command_cls.action,
                               help=command_cls.help)


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


def install_tasks():
    for task_path in exts.config['background.tasks']:
        task_cls = import_attr(task_path)
        task_cls.install()


def initialize(supervisor):
    install_extensions(supervisor)
    register_commands()
    register_menu_items()
    register_dashboard_plugins()
    register_wizard_steps()
    register_settings()


def init_complete(supervisor):
    exts.dashboard.sort()
    exts.menuitems.sort(supervisor.config)


def post_start(supervisor):
    install_tasks()
