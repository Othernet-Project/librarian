"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import view, request, redirect

from ...lib.i18n import lazy_gettext as _, i18n_path
from ...lib.validate import posint, keyof

from ..exceptions import NotSupportedError
from ..dashboard import DashboardPlugin


try:
    from . import ipc
except AttributeError:
    raise NotSupportedError('ONDD plugin requires UNIX sockets')


DELIVERY = (
    ('1', 'DVB-S'),
    ('2', 'DVB-S2'),
)

MODULATION = (
    ('qp', 'QPSK'),
    ('8p', '8PSK'),
    ('1a', '16APSK'),
    ('2a', '32APSK'),
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

# For easier consumption as view default ctx
CONST = dict(DELIVERY=DELIVERY, MODULATION=MODULATION,
             POLARIZATION=POLARIZATION)


@view('ondd/_signal')
def get_signal_stats():
    return dict(status=ipc.get_status())


@view('ondd/settings', vals={}, err={}, **CONST)
def set_settings():
    errors = {}
    original_route = request.forms.get('backto', i18n_path('/dashboard/'))
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

    if errors:
        return dict(errors=errors, vals=request.forms)

    resp = ipc.set_settings(frequency=frequency,
                            symbolrate=symbolrate,
                            delivery=delivery,
                            modulation=dict(MODULATION)[modulation],
                            voltage=VOLTS[polarization])

    if not resp.startswith('2'):
        # Translators, error message shown when setting transponder
        # configuration is not successful
        errors['_'] = _('Transponder configuration could not be set')
        return dict(errors=errors, vals=request.forms)

    redirect(original_route)


def install(app, route):
    route('/status', ['GET'], get_signal_stats)
    route('/settings', ['POST'], set_settings)


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Tuner settings')
    name = 'ondd'
    javascript = ['ondd.js']

    def get_context(self):
        return dict(status=ipc.get_status(), vals={}, errors={}, **CONST)
