import functools

from bottle import request, redirect
from bottle_utils.i18n import i18n_url


def plugin(supervisor):
    setup_path = i18n_url('setup:main')

    def plugin(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            if (not supervisor.exts.setup_wizard.is_completed and
                    request.path != setup_path[len(request.locale) + 1:]):
                return redirect(setup_path)
            return callback(*args, **kwargs)
        return wrapper
    plugin.name = 'setup'
    return plugin
