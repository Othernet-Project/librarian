import logging

from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian.librarian_core.contrib.templates.renderer import template, view

from .forms import ONDDForm

try:
    from . import ipc
except AttributeError:
    raise RuntimeError('ONDD plugin requires UNIX sockets')


@view('ondd/_signal')
def get_signal_status():
    return dict(status=ipc.get_status())


@roca_view('ondd/settings', 'ondd/_settings_form', template_func=template)
def set_settings():
    form = ONDDForm(request.forms)
    if not form.is_valid():
        return dict(form=form)

    logging.info('ONDD: tuner settings updated')
    request.app.supervisor.exts.setup.append({'ondd': form.processed_data})

    return dict(form=form,
                message=_('Transponder configuration saved.'),
                redirect_url=i18n_url('dashboard:main'))


@view('ondd/_file_list')
def show_file_list():
    return dict(files=ipc.get_file_list())


def routes(config):
    return (
        ('ondd:status', get_signal_status,
         'GET', '/ondd/status/', dict(unlocked=True, skip=['setup'])),
        ('ondd:settings', set_settings,
         'POST', '/ondd/settings/', dict(unlocked=True)),
        ('ondd:files', show_file_list,
         'GET', '/ondd/files/', dict(unlocked=True)),
    )
