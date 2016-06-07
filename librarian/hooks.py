import importlib
import logging

from bottle import error

from fsal.client import FSAL
from ondd_ipc.ipc import ONDDClient

from .core.exports import hook
from .core.exts import ext_container as exts
from .data.notifications import Notification
from .helpers.notifications import invalidate_notification_cache

from .routes import system
from .utils.filters import safepath_filter


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
    exts.notifications = Notification
    exts.notifications.on_send(invalidate_notification_cache)
    exts.ondd = ONDDClient(exts.config['ondd.socket'])


def install_tasks():
    for task_path in exts.config['background.tasks']:
        task_cls = import_attr(task_path)
        task_cls.install()


@hook('initialize')
def initialize(supervisor):
    install_extensions(supervisor)
    supervisor.app.router.add_filter('safepath', safepath_filter)
    error(403)(system.error_403)
    error(404)(system.error_404)
    error(500)(system.error_500)
    error(503)(system.error_503)


@hook('init_complete')
def init_complete(supervisor):
    exts.dashboard.sort()
    exts.menu.sort(supervisor.config)


def post_start(supervisor):
    install_tasks()
