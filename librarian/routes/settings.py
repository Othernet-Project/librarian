from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian_core.contrib.templates.renderer import template


@roca_view('settings/settings', 'settings/_settings_form',
           template_func=template)
def show_settings_form():
    settings = request.app.supervisor.exts.settings
    form_cls = settings.get_form()
    return dict(form=form_cls(),
                groups=settings.groups)


@roca_view('settings/settings', 'settings/_settings_form',
           template_func=template)
def save_settings():
    settings = request.app.supervisor.exts.settings
    form_cls = settings.get_form()
    form = form_cls(request.forms)
    if not form.is_valid():
        return dict(form=form, groups=settings.groups)

    request.app.supervisor.exts.setup.append(form.processed_data)
    request.app.supervisor.exts.events.publish('SETTINGS_SAVED',
                                               form.processed_data)
    return dict(form=form,
                groups=settings.groups,
                message=_('Settings saved.'),
                redirect_url=i18n_url('dashboard:main'))


def routes(config):
    return (
        ('settings:load', show_settings_form,
         'GET', '/settings/', dict(unlocked=True)),
        ('settings:save', save_settings,
         'POST', '/settings/', dict(unlocked=True)),
    )

