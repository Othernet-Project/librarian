import logging

from bottle_utils.i18n import lazy_gettext as _
from streamline import XHRPartialFormRoute, RouteBase

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..forms.firmware import FirmwareUpdateForm
from ..helpers.firmware import update_firmware, FIRMWARE_UPDATE_KEY
from ..utils.route_mixins import JSONResponseMixin


class FirmwareUpdate(XHRPartialFormRoute):
    name = 'firmware:update'
    path = '/firmware/'
    template_func = template
    template_name = 'firmware/update'
    partial_template_name = 'firmware/_update'
    form_factory = FirmwareUpdateForm

    def get_bound_form(self):
        form_factory = self.get_form_factory()
        return form_factory(self.request.files)

    def form_invalid(self):
        return dict(saved=False)

    def form_valid(self):
        exts.cache.set(FIRMWARE_UPDATE_KEY, 'processing')
        firmware = self.form.processed_data['firmware']
        try:
            path = exts.config['firmware.save_path']
            exts.tasks.schedule(update_firmware, args=(firmware, path))
        except Exception:
            logging.exception('Firmware upload error.')
            # Translators, shown when firmware upload failed
            return dict(saved=False,
                        message=_('Firmware upload failed.'))
        else:
            return dict(saved=True)


class FirmwareUpdateStatus(JSONResponseMixin, RouteBase):
    name = 'firmware:status'
    path = '/firmware/status/'

    def get(self):
        status = exts.cache.get(FIRMWARE_UPDATE_KEY)
        return dict(status=status)
