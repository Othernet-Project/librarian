# -*- coding: utf-8 -*-

"""
app.py: main web UI module

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals, print_function

import gevent.monkey
gevent.monkey.patch_all(aggressive=True)

# For more details on the below see: http://bit.ly/18fP1uo
import gevent.hub
gevent.hub.Hub.NOT_ERROR = (Exception,)

import os

from .core.supervisor import Supervisor


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    supervisor = Supervisor(root_dir)
    supervisor.start()


if __name__ == '__main__':
    main()
