import logging

from bottle_utils.i18n import lazy_gettext as _, i18n_url
from streamline import XHRPartialFormRoute

from ..forms import ondd as ondd_forms
from ..helpers import ondd as ondd_helpers
from ..core.contrib.templates.renderer import template


class Settings(XHRPartialFormRoute):
    path = '/ondd/settings/'
    template_func = template
    template_name = 'ondd/settings'
    partial_template_name = 'ondd/_settings_form'

    def get_form_factory(self):
        return ondd_forms.FORMS[ondd_helpers.get_band()]

    def get_default_context(self):
        band = ondd_helpers.get_band()
        ctx = super(Settings, self).get_default_context()
        ctx['band'] = band
        ctx['lband'] = ondd_helpers.LBAND
        ctx['kuband'] = ondd_helpers.KUBAND
        ctx['is_l'] = band == ondd_helpers.LBAND
        ctx['is_ku'] = band == ondd_helpers.KUBAND
        ctx['preset_keys'] = self.get_form_factory().PRESETS[0].values.keys()
        return ctx

    def form_valid(self):
        logging.info('ONDD: tuner settings updated')
        return dict(form=self.form,
                    message=_('Transponder configuration saved.'),
                    redirect_url=i18n_url('dashboard:main'))
