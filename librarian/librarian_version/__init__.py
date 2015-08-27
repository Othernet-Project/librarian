from bottle import request

from librarian import __version__
from librarian.librarian_cache.decorators import cached
from librarian.librarian_core.contrib.templates.decorators import template_helper

from .version import get_version


@template_helper
@cached()
def app_version():
    return get_version(__version__, request.app.config)
