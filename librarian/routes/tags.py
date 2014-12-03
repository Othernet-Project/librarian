import re

from bottle import default_app, request, view, redirect, template

from ..lib import archive
from ..lib.ajax import roca_view


WS = re.compile(r'\s', re.M)


@roca_view('tag_cloud', '_tag_cloud')
def tag_cloud():
    try:
        current = request.params.get('tag')
    except (ValueError, TypeError):
        current = None
    tags = archive.get_tag_cloud()
    return dict(tag_cloud=tags, tag=current)


@archive.with_content
def edit_tags(meta):
    tags = request.forms.getunicode('tags', '')
    tags = set([WS.sub(' ', t).strip() for t in tags.split(',') if t.strip()])
    existing_tags = set(meta.tags.keys())
    new = tags - existing_tags
    removed = existing_tags - tags
    archive.add_tags(meta, new)
    archive.remove_tags(meta, removed)
    if request.is_xhr:
        return template('_tag_list', meta=meta)
    redirect('/')


