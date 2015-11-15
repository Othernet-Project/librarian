import logging
import functools

from ..core import zipballs
from ..core import downloads
from ..utils.core_helpers import open_archive
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


def add_file(archive, cid, config):
    ret = archive.add_to_archive(cid)
    if ret == 0:
        logging.error('{} could not be added to library'.format(cid))
    else:
        logging.info('{} added to library'.format(cid))


def generate_file_list(app):
    read_meta = cached(app=app)(zipballs.validate)
    conf = app.config
    paths = downloads.get_downloads(conf['content.spooldir'],
                                    conf['content.output_ext'])
    return downloads.order_downloads(paths, reverse=True)


def check_for_updates(app):
    config = app.config
    meta_filename = conf['content.metadata']
    archive = open_archive(config=config)
    updates = generate_file_list(app)
    for path in updates:
        cid = zipballs.get_md5_from_path(path)
        args=(archive, cid, config)
        app.exts.tasks.schedule(add_file, args=args)
    app.exts.tasks.schedule(schedule_check, args=(app,), kwargs={'delay': 600})


def schedule_check(app, delay=10):
    app.exts.tasks.schedule(check_for_updates, args=(app,), delay=delay)


def daemon(app):
    schedule_check(app, delay=15)
