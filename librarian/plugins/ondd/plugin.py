"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from bottle import request
from bottle_utils import form
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ...utils.setup import setup_wizard
from ...utils.template import template, view
from ...utils.template_helpers import template_helper

from ..exceptions import NotSupportedError
from ..dashboard import DashboardPlugin


try:
    from . import ipc
except AttributeError:
    raise NotSupportedError('ONDD plugin requires UNIX sockets')


DELIVERY = (
    ('DVB-S', 'DVB-S'),
    ('DVB-S2', 'DVB-S2'),
)

MODULATION = (
    ('QPSK', 'QPSK'),
    ('8PSK', '8PSK'),
    ('16APSK', '16APSK'),
    ('32APSK', '32APSK'),
)

POLARIZATION = (
    # Translators, refers to transponder polarization
    ('0', _('None')),
    # Translators, refers to transponder polarization
    ('v', _('Vertical')),
    # Translators, refers to transponder polarization
    ('h', _('Horizontal')),
)

VOLTS = {
    '0': 0,
    'v': 13,
    'h': 18,
}

LNB_TYPES = (
    # Translators, this is a type of LNB
    (ipc.UNIVERSAL, _('Universal')),
    # Translators, this is a type of LNB
    (ipc.KU_BAND, _('North America Ku band')),
    # Translators, this is a type of LNB
    (ipc.C_BAND, _('C band')),
)

PRESETS = [
    ('Galaxy 19 (97.0W)', 1, {
        'frequency': '11929',
        'symbolrate': '22000',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('Hotbird 13 (13.0E)', 2, {
        'frequency': '11471',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('Intelsat 20 (68.5E)', 3, {
        'frequency': '12522',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('AsiaSat 5 C-band (100.5E)', 4, {
        'frequency': '3960',
        'symbolrate': '30000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('Eutelsat (113.0W)', 5, {
        'frequency': '12089',
        'symbolrate': '11719',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('ABS-2 (74.9E)', 6, {
        'frequency': '11734',
        'symbolrate': '44000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
    ('Intelsat 10 (47.5E)', 7, {
        'frequency': '12602',
        'symbolrate': '10110',
        'polarization': 'v',
        'delivery': 'DVB-S2',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
]


@template_helper
def get_bitrate(status):
    for stream in status.get('streams', []):
        return stream['bitrate']

    return 0


def get_file_list():
    return ipc.get_file_list()


@view('ondd/_signal')
def get_signal_status():
    return dict(status=ipc.get_status())


class ONDDForm(form.Form):
    PRESETS = PRESETS
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
        choices=LNB_TYPES
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
        choices=DELIVERY,
        # Translators, error message when wrong delivery system is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for delivery system')
            })
        ]
    )
    modulation = form.SelectField(
        _("Modulation"),
        choices=MODULATION,
        # Translators, error message when wrong modulation mode is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for modulation mode')
            })
        ]
    )
    polarization = form.SelectField(
        _("Polarization"),
        choices=POLARIZATION,
        # Translators, error message when wrong polarization is selected
        validators=[
            form.Required(messages={
                'required': _('Invalid choice for polarization')
            })
        ]
    )

    def validate(self):
        lnb = self.processed_data['lnb']
        frequency = self.processed_data['frequency']
        symbolrate = self.processed_data['symbolrate']
        delivery = self.processed_data['delivery']
        modulation = self.processed_data['modulation']
        polarization = self.processed_data['polarization']

        needs_tone = ipc.needs_tone(frequency, lnb)
        frequency = ipc.freq_conv(frequency, lnb)
        response = ipc.set_settings(frequency=frequency,
                                    symbolrate=symbolrate,
                                    delivery=delivery,
                                    tone=needs_tone,
                                    modulation=dict(MODULATION)[modulation],
                                    voltage=VOLTS[polarization])
        if not response.startswith('2'):
            # Translators, error message shown when setting transponder
            # configuration is not successful
            raise form.ValidationError('tuning_error', {})


@roca_view('ondd/settings', 'ondd/_settings_form', template_func=template)
def set_settings():
    form = ONDDForm(request.forms)
    if not form.is_valid():
        return dict(form=form)

    logging.info('ONDD: tuner settings updated')
    request.app.setup.append({'ondd': form.processed_data})

    return dict(form=form,
                message=_('Transponder configuration saved.'),
                redirect_url=i18n_url('dashboard:main'))


@view('ondd/_file_list')
def show_file_list():
    return dict(files=get_file_list())


def read_ondd_setup():
    initial_data = request.app.setup.get('ondd', {})
    return {} if isinstance(initial_data, bool) else initial_data


def has_invalid_config():
    form = ONDDForm(read_ondd_setup())
    return not form.is_valid()


@setup_wizard.register_step('ondd', template='ondd_wizard.tpl', method='GET',
                            test=has_invalid_config)
def setup_ondd_form():
    return dict(status=ipc.get_status(), form=ONDDForm())


@setup_wizard.register_step('ondd', template='ondd_wizard.tpl', method='POST',
                            test=has_invalid_config)
def setup_ondd():
    form = ONDDForm(request.forms)
    if not form.is_valid():
        return dict(successful=False, form=form, status=ipc.get_status())

    logging.info('ONDD: tuner settings updated')
    request.app.setup.append({'ondd': form.processed_data})
    return dict(successful=True)


def install(app, route):
    route(
        ('status', get_signal_status,
         'GET', '/status', dict(unlocked=True, skip=['setup'])),
        ('settings', set_settings,
         'POST', '/settings', dict(unlocked=True)),
        ('files', show_file_list,
         'GET', '/files', dict(unlocked=True)),
    )


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Tuner settings')
    name = 'ondd'
    javascript = ['ondd.js']

    def get_context(self):
        initial_data = read_ondd_setup()
        return dict(status=ipc.get_status(),
                    form=ONDDForm(initial_data),
                    files=[])
