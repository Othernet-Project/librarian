"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from bottle import (mako_view as view,
                    mako_template as template,
                    request,
                    redirect)
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ...lib.validate import posint, keyof
from ...routes.setup import setup_wizard
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
    ('u', _('Universal')),
    # Translators, this is a type of LNB
    ('k', _('North America Ku band')),
)

PRESETS = [
    ('Galaxy 19 (97.0W)', 1, {
        'frequency': '12177',
        'symbolrate': '23000',
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
    ('Intelsat 10 (47.5E)', 4, {
        'frequency': '12602',
        'symbolrate': '10110',
        'polarization': 'v',
        'delivery': 'DVB-S2',
        'modulation': 'QPSK',
        'azimuth': 0,
    }),
]

# For easier consumption as view default ctx
CONST = dict(DELIVERY=DELIVERY, MODULATION=MODULATION,
             POLARIZATION=POLARIZATION, PRESETS=PRESETS, LNB_TYPES=LNB_TYPES)


@template_helper
def get_bitrate(status):
    for stream in status.get('streams', []):
        return stream['bitrate']

    return ''


def get_file_list():
    return ipc.get_file_list()


@view('ondd/_signal')
def get_signal_status():
    return dict(status=ipc.get_status())


def validate_params(errors):
    lnb = keyof('lnb', LNB_TYPES,
                # Translators, error message when LNB type is incorrect
                _('Invalid choice for LNB type'), errors)
    frequency = posint('frequency',
                       # Translators, error message when frequency value is
                       # wrong
                       _('Frequency must be a positive number'),
                       # Translators, error message when frequency value is
                       # wrong
                       _('Please type in a number'), errors)
    symbolrate = posint('symbolrate',
                        # Translators, error message when symbolrate value is
                        # wrong
                        _('Symbolrate must be a positive number'),
                        # Translators, error message when symbolrate value is
                        # wrong
                        _('Please type in a number'), errors)
    delivery = keyof('delivery', DELIVERY,
                     # Translators, error message shown when wrong delivery
                     # system is selected
                     _('Invalid choice for delivery system'), errors)
    modulation = keyof('modulation', MODULATION,
                       # Translators, error message shown when wrong modulation
                       # mode is selected
                       _('Invalid choice for modulation mode'), errors)
    polarization = keyof('polarization', POLARIZATION,
                         # Translators, error message shown when wrong
                         # polarization is selected
                         _('Invalid choice for polarization'), errors)
    # TODO: Add support for DiSEqC azimuth value
    return dict(lnb=lnb,
                frequency=frequency,
                symbolrate=symbolrate,
                delivery=delivery,
                modulation=modulation,
                polarization=polarization)


def setup_ipc(lnb, frequency, symbolrate, delivery, modulation, polarization):
    needs_tone = ipc.needs_tone(frequency, lnb)
    frequency = ipc.freq_conv(frequency, lnb)
    return ipc.set_settings(frequency=frequency,
                            symbolrate=symbolrate,
                            delivery=delivery,
                            tone=needs_tone,
                            modulation=dict(MODULATION)[modulation],
                            voltage=VOLTS[polarization])


@roca_view('ondd/settings', 'ondd/_settings_form', template_func=template,
           vals={}, errors={}, message='', **CONST)
def set_settings():
    errors = {}
    original_route = request.forms.get('backto', i18n_url('dashboard:main'))
    params = validate_params(errors)

    if errors:
        return dict(errors=errors, vals=request.forms)

    resp = setup_ipc(**params)

    if not resp.startswith('2'):
        # Translators, error message shown when setting transponder
        # configuration is not successful
        errors['_'] = _('Transponder configuration could not be set')
        return dict(errors=errors, vals=request.forms)

    logging.info('ONDD: tuner settings updated')
    request.app.setup.append({'ondd': params})

    if request.is_xhr:
        return dict(errors={},
                    vals=request.forms,
                    message=_('Transponder configuration saved.'))

    redirect(original_route)


@view('ondd/_file_list')
def show_file_list():
    return dict(files=get_file_list())


def has_no_lock():
    status = ipc.get_status()
    return not status['has_lock']


@setup_wizard.register_step('ondd', template='ondd_wizard.tpl', method='GET',
                            test=has_no_lock)
def setup_ondd_form():
    return dict(status=ipc.get_status(), vals={}, errors={}, **CONST)


@setup_wizard.register_step('ondd', template='ondd_wizard.tpl', method='POST',
                            test=has_no_lock)
def setup_ondd():
    errors = {}
    params = validate_params(errors)

    if errors:
        return dict(successful=False,
                    errors=errors,
                    vals=request.forms,
                    status=ipc.get_status(),
                    **CONST)

    resp = setup_ipc(**params)

    if not resp.startswith('2'):
        # Translators, error message shown when setting transponder
        # configuration is not successful
        errors['_'] = _('Transponder configuration could not be set')
        return dict(successful=False,
                    errors=errors,
                    vals=request.forms,
                    status=ipc.get_status(),
                    **CONST)

    logging.info('ONDD: tuner settings updated')

    request.app.setup.append({'ondd': params})
    return dict(successful=True)


def install(app, route):
    try:
        # Test connection
        ipc.connect(app.config['ondd.socket'])
    except Exception as err:
        logging.error('ONDD: connection failed: %s', err)
        raise NotSupportedError('ONDD socket refused connection')
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
        return dict(status=ipc.get_status(),
                    vals=request.app.setup.get('ondd', {}),
                    files=get_file_list(),
                    errors={},
                    **CONST)
