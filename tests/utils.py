"""
helpers.py: Unit test helper functions

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import itertools

__all__ = ('configure', 'return_multi',)


def configure(**kwargs):
    """ Helper that provides a mock config dict """
    opts = {
        'content.spooldir': '/foo',
        'content.extension': 'sig',
        'content.keep': '12',
        'content.keyring': '/bar',
        'content.output_ext': 'zip',
        'content.metadata': 'info.json',
        'content.contentdir': '/foo',
    }
    kwargs = {'content.' + k: v for k, v in kwargs.items()}
    opts.update(kwargs)
    return opts


def return_multi(mock_object, iterable):
    """ Makes the mock object to return from the iterator """
    rvals = itertools.cycle(iterable)
    def iter_return(*args, **kwargs):
        return next(rvals)
    mock_object.side_effect = iter_return
