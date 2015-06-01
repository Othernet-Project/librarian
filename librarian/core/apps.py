"""
apps.py: helper functions for dealing with apps

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import json

from . import zipballs


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
        self.icon_behavior = behavior

    def description(self, locale, default_locale, default_description):
        default_desc = self.descriptions.get(default_locale,
                                             default_description)
        return self.descriptions.get(locale, default_desc)


def get_app_info(path):
    try:
        info = zipballs.get_file(path, 'app.json')
    except zipballs.ValidationError:
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
