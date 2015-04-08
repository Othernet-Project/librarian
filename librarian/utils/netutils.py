"""
netutils.py: Network utilities

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import socket

from bottle import request


def get_current_host():
    try:
        host, _ = request.urlparts.netloc.split(':')
    except ValueError:
        host = request.urlparts.netloc

    return host


def is_ip_address(addr):
    try:
        socket.inet_aton(addr)
    except socket.error:
        return False
    else:
        return True
