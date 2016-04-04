from bottle import request
from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from ondd_ipc.utils import needs_tone, freq_conv

from . import consts

from ..helpers.ondd import has_tuner


class ONDDForm(form.Form):
    PRESETS = consts.PRESETS
    messages = {
        'tuning_error': _("Tuner configuration could not be saved. "
                          "Please make sure that the tuner is connected.")
    }
    # TODO: Add support for DiSEqC azimuth value
    lnb = form.SelectField(
        _("LNB Type"),
        # Translators, error message when LNB type is incorrect
        validators=[form.Required(messages={
            'required': _('Invalid choice for LNB type')
        })],
        choices=consts.LNB_TYPES
    )
    frequency = form.IntegerField(
        _("Frequency"),
        validators=[
            form.Required(),
            form.InRangeValidator(
                min_value=0,
                # Translators, error message when frequency value is wrong
                messages={'min_val': _('Frequency must be a positive number')}
            )
        ]
    )
    symbolrate = form.IntegerField(
        _("Symbol rate"),
        validators=[
            form.Required(),
            form.InRangeValidator(
                min_value=0,
                # Translators, error message when symbolrate value is wrong
                messages={'min_val': _('Symbolrate must be a positive number')}
            )
        ]
    )
    delivery = form.SelectField(
        _("Delivery system"),
        choices=consts.DELIVERY,
        # Translators, error message when wrong delivery system is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for delivery system')
            })
        ]
    )
    modulation = form.SelectField(
        _("Modulation"),
        choices=consts.MODULATION,
        # Translators, error message when wrong modulation mode is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for modulation mode')
            })
        ]
    )
    polarization = form.SelectField(
        _("Polarization"),
        choices=consts.POLARIZATION,
        # Translators, error message when wrong polarization is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for polarization')
            })
        ]
    )

    def validate(self):
        if not has_tuner():
            # Translators, error message shown when a tuner is not detected
            raise form.ValidationError('tuning_error', {})

        lnb = self.processed_data['lnb']
        frequency = self.processed_data['frequency']
        symbolrate = self.processed_data['symbolrate']
        delivery = self.processed_data['delivery']
        modulation = self.processed_data['modulation']
        polarization = self.processed_data['polarization']
        settings = dict(frequency=freq_conv(frequency, lnb),
                        symbolrate=symbolrate,
                        delivery=delivery,
                        tone=needs_tone(frequency, lnb),
                        modulation=dict(consts.MODULATION)[modulation],
                        voltage=consts.VOLTS[polarization])
        ondd_client = request.app.supervisor.exts.ondd
        response = ondd_client.set_settings(**settings)
        if not response.startswith('2'):
            # Translators, error message shown when setting transponder
            # configuration is not successful
            raise form.ValidationError('tuning_error', {})
