"""
content.py: Low-level content asset management

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import re


COMP_RE = re.compile(r'([0-9a-f]{2,3})')
MD5_RE = re.compile(r'[0-9a-f]{32}')


def content_path_components(s):
    """ Extracts path components from and s or a path

    The ``s`` argument should be content ID (md5 hexdigest) or content path.

    This function returns a list of 11 components where first 10 contain 3 hex
    digits each, and last one contains only 2 digits.
    """
    if os.sep in s:
        s = s.replace(os.sep, '')
    if not MD5_RE.match(s):
        return []
    return COMP_RE.findall(s)
