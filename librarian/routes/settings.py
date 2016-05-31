from bottle_utils.i18n import lazy_gettext as _, i18n_url
from streamline import XHRPartialFormRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts


class Settings(XHRPartialFormRoute):
    path = '/settings/'
    template_func = template
    template_name = 'settings/settings'
    partial_template_name = 'settings/_settings_form'

    def get_form_factory(self):
        return exts.settings.get_form()

    def get_context(self):
        context = super(Settings, self).get_context()
        context.update(groups=exts.settings.groups)
        return context

    def form_valid(self):
        exts.setup.append(self.form.processed_data)
        exts.events.publish('SETTINGS_SAVED', self.form.processed_data)
        return dict(message=_('Settings saved.'),
                    redirect_url=i18n_url('dashboard:main'))
