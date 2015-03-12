"""
gspawn.py: Shortcut wrappers for working with greenlets

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import gevent


class TimeoutError(Exception):
    pass


def call(_callable, *args, **kwargs):
    """ Spawns a greenlet re-raising any exceptions and returning the value

    Any extra arguments and keyword arguments passed to this function will be
    passed to the callable.

    If the optional ``_timeout`` keyword argument is passed, the greenlet will
    time out after the specified number of seconds, and raise a
    ``TimeoutError`` exception.

    .. note::

        Parameters are named with an underscore prefix so they do not clash
        with any of the callable's arguments.

    :param _callable:   object to call
    :param _timeout:    optional timeout in seconds
    :returns:           value returned from the greenlet
    """
    try:
        timeout = kwargs.pop('_timeout')
    except KeyError:
        timeout = None
    g = gevent.spawn(_callable, *args, **kwargs)
    g.join(timeout=timeout)
    if timeout is not None and not g.successful():
        raise TimeoutError
    if g.exception:
        raise g.exception
    return g.value


