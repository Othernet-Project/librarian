from functools import wraps

from bottle import request
from bottle_utils.lazy import Lazy

from ..utils.core_helpers import open_archive, filter_downloads
from ..utils.notifications import Notification


def add_file(archive, file, config):
    print('+++++++++++++++++++++++++++++')
    print(1)
    notifications = Notification
    print(2)
    archive.add_to_archive(file)
    print(3)
    resp = archive.get_single(file)
    print(4)
    notifications.send({'id': resp[0], 'title': resp[2]}, category='content',
                       config=config)
    print('success')
    print('+++++++++++++++++++++++++++++')


def check_for_updates(archive, config):
    print('=== CHECKING FOR UPDATES ===')
    print('getting file list')
    file_list = [meta['md5'] for meta in filter_downloads(lang=None)]
    print(file_list)
    for file in file_list:
        args=(archive, file, config)
        print(args)
        request.app.exts.tasks.schedule(add_file, args=args)
    print('=== DONE QUEUEING ===')


def get_config(app):
    return app.config


def hook(app):
    def plugin(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            print(app)
            config = Lazy(get_config, app)
            dbs = config
            archive = open_archive(config=config, request=False)
            app.exts.tasks.schedule(
                check_for_updates, args=(
                    archive, config), delay=10, periodic=True)
            return wrapper
    plugin.name = 'import_daemon'
    return plugin


def import_plugin(app):
    print('starting import daemon')
    app.install(hook(app))
    print('started import daemon')
