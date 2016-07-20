import logging

from bottle_utils.i18n import lazy_gettext as _
from streamline import XHRPartialFormRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..forms.firmware import FirmwareUpdateForm
from ..helpers.firmware import update_firmware


class FirmwareUpdate(XHRPartialFormRoute):
    name = 'firmware:update'
    path = '/firmware'
    template_func = template
    template_name = 'firmware/update'
    partial_template_name = 'firmware/_update'
    form_factory = FirmwareUpdateForm

    def get_bound_form(self):
        form_factory = self.get_form_factory()
        return form_factory(self.request.files)

    def form_valid(self):
        firmware = self.form.processed_data['firmware']
        try:
            path = exts.config['firmware.save_path']
            update_firmware(firmware, path)
        except Exception:
            logging.exception('Firmware upload error.')
            # Translators, shown when firmware upload failed
            return dict(success=False,
                        message=_('Firmware upload failed.'))
        else:
            return dict(success=True,
                        message=_('Firmware upload successful.'))
