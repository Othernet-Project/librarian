"""
exceptions.py: plugin exceptions

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


class NotSupportedError(Exception):
    """ Raied when plugin declares itself as incomptaible

    This exception should not be allowed to propagaed, and should be silenced
    cleanly. It's considered non-fatal and app should run fine after loading
    remaining plugins.
    """
    def __init__(self, reason):
        self.reason = reason
        super(NotSupportedError, self).__init__()
