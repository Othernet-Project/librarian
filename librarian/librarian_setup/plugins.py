import functools

from bottle import request, redirect
from bottle_utils.i18n import i18n_url

from .setup import setup_wizard


def plugin(supervisor):
    setup_path = i18n_url('setup:main')
    ignored_paths = [setup_path, i18n_url('diag:main')]

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            if (not setup_wizard.is_completed and
                    not any([request.path == path[len(request.locale) + 1:]
                             for path in ignored_paths])):
                return redirect(setup_path)
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'setup'
    return plugin
