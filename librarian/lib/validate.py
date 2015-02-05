"""
validate.py: Validation functions

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request


def posint(key, notpositive, notnum, errors_dict):
    """ Validates that value is positive integer

    :param key:             key to look up in reuqest parameters
    :param notpositive:     error message when value is not positive
    :param notnum:          error message when value is not a number
    :param errors_dict:     dictionary containing errors
    """
    try:
        value = int(request.forms.get(key))
        if value < 0:
            errors_dict[key] = notpositive
    except (TypeError, ValueError):
        errors_dict[key] = notnum
    return value


def keyof(key, mapping, error, errors_dict):
    """ Validates that vlaue is a key of specified dict

    :param key:             key to look up in reuqest parameters
    :param mapping:         mapping object (dict, list of two-tuples, etc)
    :param error:           error message
    :param errors_dict:     dictionary containing errors
    """
    mapping = dict(mapping)
    value = request.forms.get(key)
    if not value or value not in mapping:
        errors_dict[key] = error
    return value

