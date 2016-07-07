from bottle import request
from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from ondd_ipc.utils import needs_tone, freq_conv

from ..helpers import ondd


class ONDDFormBase(form.Form):
    messages = {
        # Translators, error message shown when a tuner is not detected
        'tuning_error': _("Tuner configuration could not be saved. "
                          "Please make sure that the tuner is connected.")
    }

    @property
    def preset_data(self):
        index = self.processed_data.get('preset', 0)
        try:
            preset = self.PRESETS[index - 1]
        except IndexError:
            return {}
        else:
            (_, _, data) = preset
            return data


class LForm(ONDDFormBase):
    PRESETS = ondd.L_PRESETS
    preset = form.IntegerField(
        _("Satellite"),
        validators=[
            form.Required(messages={
                # Translators, message shown when user does not select a
                # satellite preset nor 'Custom' option to enter custom data.
                'required': _("Please select a satellite or select 'Custom'")
            }),
            form.InRangeValidator(min_value=0, max_value=len(PRESETS))
        ]
    )
    frequency = form.FloatField(
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
    uncertainty = form.IntegerField(
        _("Frequency uncertainty"),
        validators=[
            form.Required(),
            form.InRangeValidator(
                min_value=0,
                # Translators, error message when uncertainty value is wrong
                messages={'min_val': _('Frequency uncertainty must be a '
                                       'positive number')}
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
    sample_rate = form.FloatField(
        _("Sample rate"),
        validators=[
            form.Required(),
            form.InRangeValidator(
                min_value=0,
                # Translators, error message when sample rate is wrong
                messages={
                    'min_val': _('Sample rate must be a positive number')
                }
            )
        ]
    )
    rf_filter = form.SelectField(
        _("RF filter"),
        # Translators, error message when LNB type is incorrect
        choices=ondd.RF_FILTERS
    )
    descrambler = form.BooleanField(
        _("Descrambler"),
        default=False,
    )

    def preprocess_frequency(self, value):
        return self.preset_data.get('frequency', value)

    def preprocess_uncertainty(self, value):
        return self.preset_data.get('uncertainty', value)

    def preprocess_symbolrate(self, value):
        return self.preset_data.get('symbolrate', value)

    def preprocess_sample_rate(self, value):
        return self.preset_data.get('sample_rate', value)

    def preprocess_rf_filter(self, value):
        return float(self.preset_data.get('rf_filter', value))

    def preprocess_descrambler(self, value):
        return self.preset_data.get('descrambler', value)

    def validate(self):
        ondd.write_ondd_setup(self.processed_data)
        try:
            ondd.restart_demod()
        except ondd.DemodRestartError:
            raise form.ValidationError('tuning_error', {})


class KuForm(ONDDFormBase):
    PRESETS = ondd.KU_PRESETS
    preset = form.IntegerField(
        _("Satellite"),
        validators=[
            form.Required(messages={
                # Translators, message shown when user does not select a
                # satellite preset nor 'Custom' option to enter custom data.
                'required': _("Please select a satellite or select 'Custom'")
            }),
            form.InRangeValidator(min_value=0, max_value=len(PRESETS))
        ]
    )
    # TODO: Add support for DiSEqC azimuth value
    lnb = form.SelectField(
        _("LNB Type"),
        # Translators, error message when LNB type is incorrect
        validators=[form.Required(messages={
            'required': _('Invalid choice for LNB type')
        })],
        choices=ondd.LNB_TYPES
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
        choices=ondd.DELIVERY,
        # Translators, error message when wrong delivery system is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for delivery system')
            })
        ]
    )
    modulation = form.SelectField(
        _("Modulation"),
        choices=ondd.MODULATION,
        # Translators, error message when wrong modulation mode is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for modulation mode')
            })
        ]
    )
    polarization = form.SelectField(
        _("Polarization"),
        choices=ondd.POLARIZATION,
        # Translators, error message when wrong polarization is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for polarization')
            })
        ]
    )

    def preprocess_frequency(self, value):
        return self.preset_data.get('frequency', value)

    def preprocess_symbolrate(self, value):
        return self.preset_data.get('symbolrate', value)

    def preprocess_delivery(self, value):
        return self.preset_data.get('delivery', value)

    def preprocess_modulation(self, value):
        return self.preset_data.get('modulation', value)

    def preprocess_polarization(self, value):
        return self.preset_data.get('polarization', value)

    def validate(self):
        if not ondd.has_tuner():
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
                        modulation=dict(ondd.MODULATION)[modulation],
                        voltage=ondd.VOLTS[polarization])
        ondd_client = request.app.supervisor.exts.ondd
        response = ondd_client.set_settings(**settings)
        if not response.startswith('2'):
            # Translators, error message shown when setting transponder
            # configuration is not successful
            raise form.ValidationError('tuning_error', {})
        ondd.write_ondd_setup(self.processed_data)


FORMS = {
    ondd.LBAND: LForm,
    ondd.KUBAND: KuForm,
}
