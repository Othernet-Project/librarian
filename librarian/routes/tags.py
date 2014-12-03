import re

from bottle import default_app, request, view, redirect, template

from ..lib import archive
from ..lib.ajax import roca_view


WS = re.compile(r'\s', re.M)


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


