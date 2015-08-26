"""
security.py: security related utilities

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from .utils import generate_secret_key


def init_begin(supervisor):
    supervisor.exts.setup.autoconfigure('session.secret')(generate_secret_key)
    supervisor.exts.setup.autoconfigure('csrf.secret')(generate_secret_key)
