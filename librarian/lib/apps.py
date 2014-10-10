"""
apps.py: helper functions for dealing with apps

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import json
import zipfile

from bottle import request

from .downloads import ContentError, extract_file
from .i18n import i18n_path, lazy_gettext as _


class AppError(Exception):
    """ Base app-related exception """
    pass


class MetadataError(AppError):
    pass


class AppInfo(object):
    """ Class that wraps application metadata """
    def __init__(self, appid, title, version, descriptions={}, behavior=False):
        self.appid = appid
        self.title = title
        self.version = version
        self.descriptions = descriptions
        self.url = i18n_path('/apps/%s/' % appid)
        self.icon_behavior = behavior

    @property
    def description(self):
        default_desc = self.descriptions.get(
            # Translators, this is used when app doesn't provide a description
            request.default_locale, _('No description provided'))
        return self.descriptions.get(request.locale, default_desc)


def get_app_info(path):
    try:
        metadata, info = extract_file(path, 'app.json')
    except ContentError:
        raise MetadataError('Could not extract metadata')
    try:
        info = str(info.read().decode('utf8'))
    except UnicodeDecodeError as err:
        raise MetadataError('Could not read metadata')
    try:
        meta = json.loads(info)
    except ValueError as err:
        raise MetadataError('Could not decode metadata')
    return AppInfo(meta['id'], meta['title'], meta['version'],
                   meta['description'], meta['icon_behavior'])


