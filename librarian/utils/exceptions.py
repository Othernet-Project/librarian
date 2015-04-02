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


class ConfigurationError(Exception):
    """ Raised when application is not configured correctly """
    pass


class ConfigurationFormatError(ConfigurationError):
    """ Raised when configuration file is malformed """
    def __init__(self, keyerr):
        key = keyerr.args[0]
        if '.' in key:
            self.section, self.subsection = key.split('.')
        else:
            self.section = 'GLOBAL'
            self.subsection = key
        super(ConfigurationFormatError, self).__init__(
            "Configuration error in section [{}]: missing '{}' setting".format(
                self.section, self.subsection))
