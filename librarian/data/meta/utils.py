"""
Utility function used by the meta archive.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import datetime
import functools
import logging
import os
import subprocess

import gevent


def run_command(command, timeout, debug=False):
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    if debug:
        logging.debug('Command (%s) started at pid %s',
                      ' '.join(command),
                      process.pid)
    while process.poll() is None:
        gevent.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            if debug:
                logging.debug('Command (%s) timed out(>%s secs). Terminating.',
                              ' '.join(command),
                              timeout)
            process.kill()
            return (None, None)
    if debug:
        logging.debug('Command with pid %s ended normally with return code %s',
                      process.pid,
                      process.returncode)
    return (process.returncode, process.stdout.read())


def runnable(timeout=5, debug=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd = func(*args, **kwargs)
            return run_command(cmd, timeout=timeout, debug=debug)
        return wrapper
    return decorator


def ancestors_of(path):
    """
    Return all of ``path``'s ancestors, including ``path`` itself.
    """
    normalized = os.path.normpath(path)
    if normalized == os.path.sep:
        # if path is "/" yield only that
        yield normalized
    elif normalized == '.':
        # if path is relative root, yield empty
        yield ''
    else:
        parts = normalized.split(os.path.sep)
        if parts[0]:
            # for relative paths, relative root would be excluded without this
            yield ''
        # yield paths, in each iteration joined up to ``i``-th component
        for i in range(len(parts)):
            yield os.path.sep.join(parts[0:i + 1]) or os.path.sep
