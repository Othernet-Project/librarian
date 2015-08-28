"""
security.py: security related utilities

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from .commands import create_superuser
from .utils import generate_secret_key

from librarian.librarian_setup.decorators import autoconfigure


autoconfigure('session.secret')(generate_secret_key)
autoconfigure('csrf.secret')(generate_secret_key)


def initialize(supervisor):
    supervisor.exts.commands.register('superuser',
                                      create_superuser,
                                      '--su',
                                      action='store_true')
    supervisor.exts.commands.register('noauth',
                                      None,
                                      '--no-auth',
                                      action='store_true',
                                      help='disable authentication')
