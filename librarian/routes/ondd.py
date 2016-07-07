import logging

from bottle_utils.i18n import lazy_gettext as _, i18n_url
from bottle_utils.lazy import Lazy
from streamline import XHRPartialRoute, XHRPartialFormRoute

from ..forms import ondd as ondd_forms
from ..helpers import ondd as ondd_helpers
from ..core.exts import ext_container as exts
from ..core.contrib.templates.renderer import template


class Status(XHRPartialRoute):
    path = '/ondd/status/'
    template_func = template
    template_name = 'ondd/_status'
    partial_template_name = 'ondd/_status'
    exclude_plugins = ['session_plugin', 'user_plugin', 'setup_plugin']

    def get(self):
        snr_min = self.config.get('ondd.snr_min', 0.2)
        snr_max = self.config.get('ondd.snr_max', 0.9)
        return dict(status=exts.ondd.get_status(),
                    SNR_MIN=snr_min,
                    SNR_MAX=snr_max)


class FileList(XHRPartialRoute):
    path = '/ondd/files/'
    template_func = template
    template_name = 'ondd/_file_list'
    partial_template_name = 'ondd/_file_list'
    exclude_plugins = ['session_plugin', 'user_plugin', 'setup_plugin']

    def get(self):
        return dict(files=exts.ondd.get_transfers())


class CacheStatus(XHRPartialRoute):
    path = '/ondd/cache/'
    template_func = template
    template_name = 'ondd/_cache_status'
    partial_template_name = 'ondd/_cache_status'
    exclude_plugins = ['session_plugin', 'user_plugin', 'setup_plugin']

    def get(self):
        cache_max = self.config['ondd.cache_quota']
        default = {'total': cache_max,
                   'free': cache_max,
                   'used': 0,
                   'alert': False}
        cache_status = exts.cache.get('ondd.cache') or default
        return dict(cache_status=cache_status)


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
