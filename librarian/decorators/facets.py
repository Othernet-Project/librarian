import functools

from bottle import abort, request
from bottle_utils.html import urlunquote

from .facets.facets import Facets
from .facets.archive import FacetsArchive


def with_facets(abort_if_not_found=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(path, **kwargs):
            path = urlunquote(path)
            conf = request.app.config
            archive = FacetsArchive(request.app.supervisor.exts.fsal,
                                    request.db.facets,
                                    config=conf)
            data = archive.get_facets(path)
            if not data:
                if abort_if_not_found:
                    abort(404)
                return func(path=path, facets=None, **kwargs)

            facets = Facets(request.app.supervisor, data.path, data=data)
            return func(path=path, facets=facets, **kwargs)
        return wrapper
    return decorator
