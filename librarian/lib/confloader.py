"""
confloader.py: Application configuration loader

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re

try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser


FLOAT_RE = re.compile(r'^\d+\.\d+$')
INT_RE = re.compile(r'^\d+$')
SIZE_RE = re.compile(r'^\d+(\.\d{1,3})? ?[KMG]B$', re.I)
FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}


def parse_size(size):
    """ Parses size with B, K, M, or G suffix and returns in size bytes

    :param size:    human-readable size with suffix
    :returns:       size in bytes or 0 if source string is using invalid
                    notation
    """
    size = size.lower()[:-1]
    if size[-1] not in 'bkmg':
        suffix = 'b'
    else:
        suffix = size[-1]
        size = size[:-1]
    try:
        size = float(size)
    except ValueError:
        return 0
    return size * FACTORS[suffix]


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


class ConfDict(dict):

    def __getitem__(self, key):
        try:
            return super(ConfDict, self).__getitem__(key)
        except KeyError as err:
            raise ConfigurationFormatError(err)

    @classmethod
    def from_file(cls, path, skip_clean=False, base_dir='.', **defaults):
        path = os.path.normpath(os.path.join(base_dir, path))
        self = cls()
        self.update(defaults)
        parser = ConfigParser()
        parser.read(path)
        sections = parser.sections()
        if not sections:
            raise ConfigurationError(
                "Missing or empty configuration file at '{}'".format(path))

        children = []
        defaults = []
        for section in sections:
            for key, value in parser.items(section):
                if section not in ('DEFAULT', 'bottle'):
                    compound_key = '{}.{}'.format(section, key)
                else:
                    compound_key = key

                if not skip_clean:
                    value = self.clean_value(value)

                if section == 'config' and key == 'defaults':
                    defaults = value
                elif section == 'config' and key == 'include':
                    children = value
                else:
                    self[compound_key] = value

        incl_basedir = os.path.dirname(path)

        for default in defaults:
            self.setdefaults(cls.from_file(default, skip_clean=skip_clean,
                                           base_dir=incl_basedir))
        for child in children:
            self.update(cls.from_file(child, skip_clean=skip_clean,
                                      base_dir=incl_basedir))
        return self

    def setdefaults(self, other):
        for k in other:
            if k in self:
                continue
            self[k] = other[k]

    @staticmethod
    def clean_value(val):
        """ Perform coercing of the values """

        # True values: 'yes', 'Yes', 'true', 'True'
        if val.lower() in ('yes', 'true'):
            return True

        # False values: 'no', 'No', 'false', 'False'
        if val.lower() in ('no', 'false'):
            return False

        # Null values: 'null', 'NULL', 'none', 'None'
        if val.lower() in ('null', 'none'):
            return None

        # Floating point numbers: 1.0, 12.443, 1002.3
        if FLOAT_RE.match(val):
            return float(val)

        # Integer values: 1, 30, 445
        if INT_RE.match(val):
            return int(val)

        # Data sizes: 10B, 12.3MB, 5.6 GB
        if SIZE_RE.match(val):
            return parse_size(val)

        # Lists: one item per line, indented
        if val.startswith('\n'):
            return val[1:].split('\n')

        # Multi-line string: same as python with triple-doublequotes
        if val.startswith('"""'):
            return val.strip('"""').strip()

        # Everything else is returned as is
        return val
