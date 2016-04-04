#!/usr/bin/python2

"""
diagnostics.py: Script/library for collecting system information

Copyright 2015 Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import print_function

import os
import time
import datetime
import platform
from glob import glob
from subprocess import check_output, CalledProcessError

NL = '\n'
SEP1 = '=' * 80 + NL
SEP2 = '-' * 80 + NL
DVB = 0
FE = 0
FRONTEND = '/dev/dvb/adapter{}/frontend{}'.format(DVB, FE)
I2C = '/sys/class/dvb/dvb{}.frontend{}/device/i2c-0/name'.format(DVB, FE)
LIBRARIAN_LOGS = ('/var/log/librarian.log', '/mnt/data/log/librarian.log',)
FSAL_LOG = ('/var/log/fsal.log', '/mnt/data/log/fsal.log',)
SYSLOG = ('/var/log/syslog', '/var/log/messages')
VERSION_FILE = '/etc/version'
NO_LOGS = 'NO LOGS FOUND'
ONDD_SOCKET = '/var/run/ondd.ctrl'


# Helpers

def shell(cmd, default='n/a'):
    """
    Call a shell command using ``check_output`` and return the output. On
    error, return default value.
    """
    try:
        return check_output(cmd, shell=True)
    except CalledProcessError:
        return default


def read_file(path):
    """
    Return file contents or empty string if file does not exist.
    """
    try:
        with open(path) as f:
            return f.read()
    except (OSError, IOError):
        return ''


def grep(s, keyword):
    """
    Return only lines of a string which contains specified keyword.
    """
    for l in s.split('\n'):
        if keyword not in l:
            continue
        yield l


def grep_file(path, keyword=None):
    """
    Return only lines of a file which contains specified keyword.
    """
    if not path or not os.path.isfile(path):
        yield NO_LOGS
        return
    with open(path) as f:
        if not keyword:
            yield f.read()
            return
        for line in f:
            if keyword in line:
                yield line.strip()


def section(name, contents):
    """
    Generate section text for the report.
    """
    return ''.join([
        SEP1,
        name, NL,
        SEP2,
        contents, NL,
        SEP1])


def find_first(paths):
    """
    Return the first path from the list that exists.
    """
    return next((p for p in paths if os.path.exists(p)), None)


# Report generation functions


def get_platform_data():
    data = []
    data.append('Name: {}'.format(platform.node()))
    data.append('Arch: {}'.format(platform.machine()))
    data.append('Version: {}'.format(read_file(VERSION_FILE)))
    data.append(shell('uptime').strip())
    return NL.join(data)


def get_mem_data():
    return shell('free -m')


def get_disk_data():
    data = []
    data.append('Mount points:')
    data.append(read_file('/proc/mounts'))
    data.append('Disk space:')
    data.append(shell('df -h'))
    return NL.join(data)


def get_proc_data():
    data = []
    psax = shell('ps ax')
    data.append(NL.join(grep(psax, 'librarian')))
    data.append(NL.join(grep(psax, 'fsal')))
    data.append(NL.join(grep(psax, 'ondd')))
    data.append(NL.join(grep(psax, 'lighttpd')))
    data.append(NL.join(grep(psax, 'monitor')))
    data.append(NL.join(grep(psax, 'postgres')))
    return NL.join(data)


def get_dmesg():
    """
    Return last 100 lines of kernel messages.
    """
    return shell('dmesg')


def get_tuner():
    return read_file(I2C)


def get_frontend_data():
    data = []
    if os.path.exists(FRONTEND):
        data.append('Frontend: {}'.format(FRONTEND))
        data.append('Device name: {}'.format(get_tuner() or 'n/a'))
    else:
        data.append('Frontend: n/a')
    return NL.join(data)


def get_network_data():
    return shell('ip addr').strip()


def get_log(path, kw=None):
    if not os.path.isfile(path):
        return NO_LOGS
    s = ''
    for f in reversed(glob(path + '*')):
        s += NL.join(grep_file(f, kw))
    return s


# Business end

def generate_report(syslog, librarian_log, fsal_log, ondd_socket):
    start = time.time()
    reports = []
    reports.append(section('Platform', get_platform_data()))
    reports.append(section('Memory', get_mem_data()))
    reports.append(section('Processes', get_proc_data()))
    reports.append(section('Kernel', get_dmesg()))
    reports.append(section('Tuner', get_frontend_data()))
    reports.append(section('Storage', get_disk_data()))
    reports.append(section('Network', get_network_data()))
    reports.append(section('ONDD', get_log(syslog, 'ondd')))
    reports.append(section('Hotplug', get_log(syslog, 'hotplug')))
    reports.append(section('Monitor', get_log(syslog, 'outernet.monitor')))
    reports.append(section('Librarian', get_log(librarian_log)))
    reports.append(section('FSAL', get_log(fsal_log)))
    if os.path.exists('/tmp/setup'):
        reports.append(section('Setup', get_log('/tmp/setup')))
    total_time = time.time() - start
    now = datetime.datetime.utcnow()
    reports.append('Generated at {}. Took {}ms.'.format(
        now.isoformat(), round(total_time * 1000, 3)))
    return NL.join(reports)


def main():
    syslog = find_first(SYSLOG)
    librarian_log = find_first(LIBRARIAN_LOGS)
    fsal_log = find_first(FSAL_LOG)
    print(generate_report(
        syslog, librarian_log, fsal_log, ONDD_SOCKET))


if __name__ == '__main__':
    main()
