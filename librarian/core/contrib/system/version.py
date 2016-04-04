"""
version.py: Provides precise Librarian version information

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import importlib

from bottle import request

from ..cache.decorators import cached
from ..templates.decorators import template_helper


def get_base_version(config):
    try:
        source = config['version.source']
    except KeyError:
        return None
    else:
        try:
            mod = importlib.import_module(source)
            return mod.__version__
        except Exception:
            return None


def get_version(config):
    version = get_base_version(config)
    if not version:
        return ''

    platform_name = config.get('platform.name', '')
    version_file = config.get('platform.version_file', '')
    try:
        with open(version_file, 'r') as v_file:
            platform_version = v_file.read().strip()
    except IOError:
        if platform_name:
            return '{0} / {1}'.format(version, platform_name)
        return version
    else:
        return '{0} / {1} {2}'.format(version, platform_name, platform_version)


@template_helper
@cached()
def app_version():
    return get_version(request.app.config)
