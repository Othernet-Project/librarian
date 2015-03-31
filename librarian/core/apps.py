"""
apps.py: helper functions for dealing with apps

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json

from bottle import request
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from .downloads import ContentError, extract_file


class AppError(Exception):
    """ Base app-related exception """
    pass


class MetadataError(AppError):
    pass


class AppInfo(object):
    """ Class that wraps application metadata """
    # XXX: Could this be a subclass of ``librarian.core.metadata.Meta?
    def __init__(self, appid, title, author, version, descriptions={},
                 behavior=False):
        self.appid = appid
        self.title = title
        self.author = author
        self.version = version
        self.descriptions = descriptions
        self.url = i18n_url('apps:app', appid=appid)
        self.icon_behavior = behavior

    @property
    def description(self):
        default_desc = self.descriptions.get(
            # Translators, this is used when app doesn't provide a description
            request.default_locale, _('No description provided'))
        return self.descriptions.get(request.locale, default_desc)

    def asset_url(self, path):
        return i18n_url('apps:asset', appid=self.appid, path=path)


def get_app_info(path):
    try:
        metadata, info = extract_file(path, 'app.json')
    except ContentError:
        raise MetadataError('Could not extract metadata')
    try:
        info = str(info.decode('utf8'))
    except UnicodeDecodeError:
        raise MetadataError('Could not read metadata')
    try:
        meta = json.loads(info)
    except ValueError:
        raise MetadataError('Could not decode metadata')
    try:
        return AppInfo(
            appid=meta['id'],
            title=meta['title'],
            author=meta['author'],
            version=meta['version'],
            descriptions=meta['description'],
            behavior=meta['icon_behavior'])
    except KeyError:
        raise MetadataError('Incomplete metadata')
