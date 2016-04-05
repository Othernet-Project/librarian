from bottle import request

from ..core.contrib.auth.options import Options
from ..core.contrib.i18n.utils import set_current_locale


@Options.collector('language')
def collect_language(options):
    return request.locale


@Options.processor('language', is_explicit=True)
def process_language(options, language):
    if language and request.locale != language:
        set_current_locale(language)


@Options.processor('default_route')
def process_default_route(options, default_route):
    if default_route:
        request.default_route = default_route
