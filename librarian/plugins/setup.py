import functools

from bottle import request, redirect
from bottle_utils.i18n import i18n_url

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts


NO_XHR_TEMPLATE = 'setup/no_xhr.tpl'


def setup_plugin(fn):
    """
    On incoming requests, check if the setup process has been already completed
    and in case it wasn't, redirect to the setup wizard.

    Exclusions to this rule are paths belonging to the setup wizard itself and
    static paths.
    """
    setup_path = i18n_url('setup:enter')
    excluded_paths = [setup_path, i18n_url('setup:diag')]
    is_excluded = lambda: any(request.path == path[len(request.locale) + 1:]
                              for path in excluded_paths)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not exts.setup_wizard.is_completed and not is_excluded():
            return (template(NO_XHR_TEMPLATE)
                    if request.is_xhr else redirect(setup_path))
        return fn(*args, **kwargs)
    return wrapper
setup_plugin.name = 'setup'
