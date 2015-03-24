"""
patch_content.py: Utility functions for patching content HTML

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re


STYLE_LINK = '<link rel="stylesheet" href="/static/css/content.css">'


def patch(html):
    """ Patch HTML adding it the content stylesheet

    The patching perofrmed by this function is pretty basic. Its goal is not to
    be overly robust or even correct. It is assumed that content would be
    authored correctly to begin with.

    :param html:    HTML to be patched
    :returns:       patched HTML
    """
    html = html.decode('utf8')
    if not re.search(r'<html>[\s\S\n\r]*</html>', html, re.M):
        html = '<html>%s</html>' % html
    if not re.search(r'<head>[\s\S\n\r]*</head>', html, re.M):
        html = html.replace('<html>', '<html><head></head>')
    html = html.replace('</head>', STYLE_LINK + '</head>')
    return len(html), html
