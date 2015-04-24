"""
tags.py: Routes related to tags and tagging

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re

from bottle import request, redirect, mako_template as template
from bottle_utils.ajax import roca_view

from .helpers import open_archive, with_content


WS = re.compile(r'\s', re.M)


def split_tags(tags):
    tags = (t.strip() for t in tags.split(','))
    return set([WS.sub(' ', t) for t in tags if t])


@roca_view('tag_cloud', '_tag_cloud', template_func=template)
def tag_cloud():
    base_path = request.params.get('base_path')
    try:
        current = request.params.get('tag')
    except (ValueError, TypeError):
        current = None
    archive = open_archive()
    tags = archive.get_tag_cloud()
    return dict(tag_cloud=tags, tag=current, base_path=base_path)


@with_content
def edit_tags(meta):
    base_path = request.params.get('base_path')
    tags = request.forms.getunicode('tags', '')
    tags = split_tags(tags)
    existing_tags = set(meta.tags.keys())
    new = tags - existing_tags
    removed = existing_tags - tags
    archive = open_archive()
    archive.add_tags(meta, new)
    archive.remove_tags(meta, removed)
    if request.is_xhr:
        return template('_tag_list', meta=meta, base_path=base_path)
    redirect('/')
