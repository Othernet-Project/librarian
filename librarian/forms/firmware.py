from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _


class FirmwareUpdateForm(form.Form):
    firmware = form.FileField(
        _("Firmware"),
        validators=[
            form.Required(messages={
                # Translators, shown as a prompt to user in dashboard
                'required': _('Please select the firmware')
            })
        ]
    )
