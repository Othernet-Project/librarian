"""
sysuser.py: System user management under Linux

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import subprocess


# Commands
PREFIX = '/usr/sbin'
DELUSER = PREFIX + '/deluser'
ADDUSER = PREFIX + '/adduser'
PASSWD = PREFIX + '/passwd'

# Account parameters
HOME = '/home/outernet'
UID = '1000'  # must be str for subprocess.Popen
SHELL = '/bin/sh'
SUDO_GROUP = 'sudo'


def deluser(username):
    """
    Delete an existing system user
    """
    ret = subprocess.call([DELUSER, username])
    if ret:
        raise RuntimeError("could not delete account '{}'".format(username))


def adduser(username, password):
    """
    Add a new system user and set its password
    """
    p = subprocess.Popen([ADDUSER, '-u', UID, '-s', SHELL, '-h', HOME,
                          '-G', SUDO_GROUP, username], stdin=subprocess.PIPE)
    p.communicate('{pw}\n{pw}\n'.format(pw=password))
    if not p.returncode == 0:
        raise RuntimeError("Could not create account '{}'".format(username))


def replace_user(existing, username, password):
    """
    Replace existing user with a completely new user account

    Shortcut for doing ``deluser()`` and ``adduser()`` in one go.
    """
    deluser(existing)
    adduser(username, password)
