from functools import wraps

from bottle import request, abort

from .helpers import metadata, content_mod, open_archive


def with_content(func):
    @wraps(func)
    def wrapper(content_id, **kwargs):
        conf = request.app.config
        archive = open_archive()
        try:
            content = archive.get_single(content_id)
        except IndexError:
            abort(404)
        if not content:
            abort(404)
        content_dir = conf['library.contentdir']
        content_path = content_mod.to_path(content_id, prefix=content_dir)
        meta = metadata.Meta(content, content_path)
        return func(meta=meta, **kwargs)
    return wrapper
