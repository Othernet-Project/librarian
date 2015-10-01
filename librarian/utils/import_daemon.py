import logging
import functools

from ..core import zipballs
from ..core import downloads
from ..utils.core_helpers import open_archive
from ..utils.notifications import Notification
from ..utils.cache import generate_key


def cached(app, prefix='', timeout=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not app.exts.is_installed('cache'):
                return func(*args, **kwargs)

            backend = app.exts.cache
            generated = generate_key(func.__name__, *args, **kwargs)
            parsed_prefix = backend.parse_prefix(prefix)
            key = '{0}{1}'.format(parsed_prefix, generated)
            value = backend.get(key)
            if value is None:
                # not found in cache, or is expired, recalculate value
                value = func(*args, **kwargs)
                expires_in = timeout
                if expires_in is None:
                    expires_in = backend.default_timeout
                backend.set(key, value, timeout=expires_in)
            return value
        return wrapper
    return decorator


def add_file(archive, file, config):
    print('+++++++++++++++++++++++++++++')
    print(file)
    notifications = Notification
    archive.add_to_archive(file)
    resp = archive.get_single(file)
    notifications.send({'id': resp[0], 'title': resp[2]}, category='content',
                       db=config['db']['sessions'])
    print('success')
    print('+++++++++++++++++++++++++++++')


def generate_file_list(app):
    read_meta = cached(app=app)(zipballs.validate)
    conf = app.config
    paths = downloads.get_downloads(conf['content.spooldir'],
                                    conf['content.output_ext'])
    zballs = list(reversed(downloads.order_downloads(paths)))
    meta_filename = conf['content.metadata']
    metas = []
    for zipball_path, timestamp in zballs:
        try:
            # if this works it's valid, we don't need the info though
            read_meta(zipball_path, meta_filename=meta_filename)
        except zipballs.ValidationError:
            # file is probably in progress, ignore it
            pass
        metas.append(zipballs.get_md5_from_path(zipball_path))
    return metas


def check_for_updates(app):
    config = app.config
    archive = open_archive(config=config)
    file_list = generate_file_list(app)
    logging.info('Found {0} updates'.format(len(file_list)))
    for file in file_list:
        args=(archive, file, config)
        app.exts.tasks.schedule(add_file, args=args)


def daemon(app):
    app.exts.tasks.schedule(check_for_updates, args=(app,), delay=10,
                            periodic=False)
