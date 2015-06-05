"""
lock.py: Install lock plugin

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from ..lib import lock


def lock_plugin(app):
    app.install(lock.lock_plugin)
