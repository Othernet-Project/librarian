"""
tags.py: Routes related to tags and tagging

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re

from bottle import request, redirect
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import i18n_url

from ..utils.core_helpers import open_archive, with_content
from ..utils.template import template


WS = re.compile(r'\s', re.M)


def split_tags(tags):
    tags = (t.strip() for t in tags.split(','))
    return set([WS.sub(' ', t) for t in tags if t])


@roca_view('tag_cloud', '_tag_cloud', template_func=template)
def tag_cloud():
    # base_path is used to construct a link to content list or sites page
    # filtered by tag (see _tag_list.tpl).
    base_path = request.params.get('base_path', i18n_url('content:list'))
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
    request.app.exts.cache.invalidate('content')
    if request.is_xhr:
        return template('_tag_list', meta=meta, base_path=base_path)
    redirect('/')


def routes(app):
    return (
        ('tags:list', tag_cloud, 'GET', '/tags/', {}),
        ('tags:edit', edit_tags, 'POST', '/tags/<content_id>', {}),
    )
