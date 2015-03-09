import re

from bottle import request, redirect, template

from ..core import archive

from ..lib.ajax import roca_view


WS = re.compile(r'\s', re.M)


def split_tags(tags):
    tags = (t.strip() for t in tags.split(','))
    return set([WS.sub(' ', t) for t in tags if t])


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
    tags = split_tags(tags)
    existing_tags = set(meta.tags.keys())
    new = tags - existing_tags
    removed = existing_tags - tags
    archive.add_tags(meta, new)
    archive.remove_tags(meta, removed)
    if request.is_xhr:
        return template('_tag_list', meta=meta)
    redirect('/')


