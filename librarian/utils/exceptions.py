"""
exceptions.py: Application-wide exception classes

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


class AppWarning(RuntimeWarning):
    """ Generic application warning """
    pass


class AppStartupWarning(AppWarning):
    """ Warnings related to startup configuration """
    pass
