"""
helpers.py: librarian core helper functions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from datetime import datetime
from functools import wraps
from urlparse import urljoin

from bottle import request, redirect, abort
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from ..core import content as content_mod
from ..core import downloads
from ..core import metadata
from ..core import zipballs
from ..core.archive import Archive
from ..core.files import FileManager
from ..utils.cache import cached

from .lang import SELECT_LANGS
from .netutils import IPv4Range, get_target_host
from .system import ensure_dir
from .template_helpers import template_helper


LICENSES = (
    (None, _('Unknown license')),
    ('CC-BY', _('Creative Commons Attribution')),
    ('CC-BY-ND', _('Creative Commons Attribution-NoDerivs')),
    ('CC-BY-NC', _('Creative Commons Attribution-NonCommercial')),
    ('CC-BY-ND-NC', _('Creative Commons Attribution-NonCommercial-NoDerivs')),
    ('CC-BY-SA', _('Creative Commons Attribution-ShareAlike')),
    ('CC-BY-NC-SA', _('Creative Commons Attribution-NonCommercial-ShareAlike')),
    ('GFDL', _('GNU Free Documentation License')),
    ('OPL', _('Open Publication License')),
    ('OCL', _('Open Content License')),
    ('ADL', _('Against DRM License')),
    ('FAL', _('Free Art License')),
    ('PD', _('Public Domain')),
    ('OF', _('Other free license')),
    ('ARL', _('All rights reserved')),
    ('ON', _('Other non-free license')),
)


read_meta = cached()(zipballs.validate)


def open_archive():
    conf = request.app.config
    return Archive.setup(conf['librarian.backend'],
                         request.db.main,
                         unpackdir=conf['content.unpackdir'],
                         contentdir=conf['content.contentdir'],
                         spooldir=conf['content.spooldir'],
                         meta_filename=conf['content.metadata'])


def init_filemanager():
    return FileManager(request.app.config['content.filedir'])


def with_content(func):
    @wraps(func)
    def wrapper(content_id, **kwargs):
        conf = request.app.config
        archive = open_archive()
        try:
            content = archive.get_single(content_id)
        except IndexError:
            abort(404)
        if not content:
            abort(404)
        content_dir = conf['content.contentdir']
        content_path = content_mod.to_path(content_id, prefix=content_dir)
        meta = metadata.Meta(content, content_path)
        return func(meta=meta, **kwargs)
    return wrapper


@cached(prefix='downloads', timeout=30)
def get_download_paths():
    paths = downloads.get_downloads(request.app.config['content.spooldir'],
                                    request.app.config['content.output_ext'])
    return list(reversed(downloads.order_downloads(paths)))


@cached(prefix='downloads', timeout=30)
def filter_downloads(lang):
    conf = request.app.config
    zballs = get_download_paths()
    logging.info('Found {0} updates'.format(len(zballs)))
    # Collect metadata of valid zipballs. If a language filter is specified
    # filter the list based on that.
    meta_filename = conf['content.metadata']
    metas = []
    for zipball_path, timestamp in zballs:
        try:
            meta = read_meta(zipball_path, meta_filename=meta_filename)
        except zipballs.ValidationError as exc:
            # Zip file is invalid. This means that the file is corrupted or the
            # original file was signed with corrupt data in it. Either way, we
            # don't know what to do with the file so we'll remove it.
            logging.error("Error reading: {0}: {1}".format(zipball_path, exc))
            downloads.safe_remove(zipball_path)
        else:
            if lang and meta['language'] != lang:
                continue

            meta['md5'] = zipballs.get_md5_from_path(zipball_path)
            meta['ftimestamp'] = datetime.fromtimestamp(timestamp)
            metas.append(metadata.Meta(meta, zipball_path))

    archive = open_archive()
    archive.add_replacement_data(metas, needed_keys=('title',))
    return metas


def get_content_url(root_url, domain):
    conf = request.app.config
    archive = Archive.setup(conf['librarian.backend'],
                            request.db.main,
                            unpackdir=conf['content.unpackdir'],
                            contentdir=conf['content.contentdir'],
                            spooldir=conf['content.spooldir'],
                            meta_filename=conf['content.metadata'])
    matched_contents = archive.content_for_domain(domain)
    try:
        # as multiple matches are possible, pick the first one
        meta = matched_contents[0]
    except IndexError:
        # invalid content domain
        path = 'content-not-found'
    else:
        base_path = i18n_url('content:reader', content_id=meta.md5)
        path = '{0}?path={1}'.format(base_path, request.path)

    return urljoin(root_url, path)


def content_resolver_plugin(root_url, ap_client_ip_range):
    """Load content based on the requested domain"""
    ip_range = IPv4Range(*ap_client_ip_range)

    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            target_host = get_target_host()
            is_regular_access = target_host in root_url
            if not is_regular_access and request.remote_addr in ip_range:
                # a content domain was entered(most likely), try to load it
                content_url = get_content_url(root_url, target_host)
                return redirect(content_url)
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def create_directories(app):
    ensure_dir(app.config['content.spooldir'])
    ensure_dir(app.config['content.appdir'])
    ensure_dir(app.config['content.unpackdir'])
    ensure_dir(app.config['content.contentdir'])
    ensure_dir(app.config['content.covers'])


def content_domain_plugin(app):
    app.install(content_resolver_plugin(
        root_url=app.config['librarian.root_url'],
        ap_client_ip_range=app.config['librarian.ap_client_ip_range']
    ))


@template_helper
def get_content_path(content_id):
    """ Return relative path of a content based on it's id """
    return content_mod.to_path(content_id)


@template_helper
@cached(prefix='content')
def content_languages():
    conf = request.app.config
    archive = Archive.setup(conf['librarian.backend'],
                            request.db.main,
                            unpackdir=conf['content.unpackdir'],
                            contentdir=conf['content.contentdir'],
                            spooldir=conf['content.spooldir'],
                            meta_filename=conf['content.metadata'])
    content_langs = archive.get_content_languages()
    return [(code, name) for (code, name) in SELECT_LANGS
            if code in content_langs]


@template_helper
@cached(prefix='downloads')
def download_languages():
    downloads = filter_downloads(lang=None)
    download_langs = [meta['language'] for meta in downloads]
    return [(code, name) for (code, name) in SELECT_LANGS
            if code in download_langs]


@template_helper
def readable_license(license_code):
    return dict(LICENSES).get(license_code, LICENSES[0][1])


@template_helper
def i18n_attrs(lang):
    s = ''
    if lang:
        # XXX: Do we want to keep the leading space?
        s += ' lang="%s"' % lang
    if template_helper.is_rtl(lang):
        s += ' dir="rtl"'
    return s


@template_helper
def is_free_license(license):
    return license not in ['ARL', 'ON']
