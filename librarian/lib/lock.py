"""
lock.py: Functions and plugins for global locking

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import functools
import contextlib
from time import sleep

from bottle import request, abort


class LockFailureError(Exception):
    """ Raised when lock fails """
    pass


class UnlockFailureError(Exception):
    """ Raised when unlock fails """
    pass


def get_lock_path():
    """ Return path of the lock file """
    return request.app.config['librarian.lockfile']


def is_locked():
    """ Return True if global lock exists """
    return os.path.exists(get_lock_path())


def do_lock(attempts, timeout):
    """ Attempt to lock """
    if not attempts:
        raise LockFailureError('Could not acquire global lock')
    if is_locked():
        sleep(timeout)
        return do_lock(attempts - 1, timeout)
    open(get_lock_path(), 'w').close()


def do_release():
    """ Release the lock

    Do not call this function directly, ever. Calling this function can force
    release, which defeats the purpose of locking.
    """
    os.unlink(get_lock_path())


@contextlib.contextmanager
def global_lock(attempts=2, timeout=5, always_release=False):
    """ Provide locked context

    This context manager can be used to run code that needs the rest of the app
    to be locked down. The context manager throws a ``LockFailureError``
    exception if the lock cannot be acquired after the specified number of
    attempts.

    Lock is automatically released when execution exists the context. Raising
    exceptions inside the context will not release the lock, however. The
    ``always_release`` argument can be used to change this behavior. Exception
    from within context is always reraised regardless of whether lock is
    released or not.

    :param attempts:        number of attempts before throwing
                            ``LockFailureError``
    :param timeout:         number of seconds to wait between attempts
    :param always_release:  whether to release the lock even if there are
                            exceptions
    """
    do_lock(attempts, timeout)
    assert is_locked(), 'Expected global lock file to be present'
    try:
        yield
    except Exception:
        if always_release:
            do_release()
        raise
    do_release()
    assert not is_locked(), 'Expected global lock to be released'


def lock_plugin(callback):
    @functools.wraps(callback)
    def wrapper(*args, **kwargs):
        unlocked = request.route.config.get('unlocked', False)
        if not unlocked and is_locked():
            abort(503, 'Librarian is locked')
        return callback(*args, **kwargs)
    return wrapper

