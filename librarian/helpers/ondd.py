import os
import logging
import subprocess
from collections import namedtuple

from bottle_utils.i18n import lazy_gettext as _

import ondd_ipc.consts as ondd_consts

from ..core.exts import ext_container as exts
from ..core.contrib.templates.decorators import template_helper

LBAND = 'l'
KUBAND = 'ku'

#: The key in the application settings JSON file that contains the tuner params
SETTINGS_KEYS = {
    'l': 'ondd_l',
    'ku': 'ondd'
}

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
    (ondd_consts.UNIVERSAL, _('Universal')),
    # Translators, this is a type of LNB
    (ondd_consts.KU_BAND, _('North America Ku band')),
    # Translators, this is a type of LNB
    (ondd_consts.C_BAND, _('C band')),
)

RF_FILTERS = (  # EBW%
    ('0.1', '10%'),
    ('0.2', '20%'),
    ('0.4', '40%')
)

Preset = namedtuple('Preset', ('label', 'index', 'values'))

L_PRESETS = [
    # Translators, name of the L-band tuner preset covering most of the world
    Preset(_('Global'), 1, {
        'frequency': '1539.8725',
        'uncertainty': '4000',
        'symbolrate': '8400',
        'sample_rate': '1',
        'rf_filter': '0.2',
        'descrambler': True,
        # Translators, used as coverage area of a transponder
        'coverage': _('Europe, Africa, Asia'),
    }),
    # Translators, name of the L-band tuner preset covering the Americas
    Preset(_('Americas'), 2, {
        'frequency': '1539.8725',
        'uncertainty': '4000',
        'symbolrate': '4200',
        'sample_rate': '1',
        'rf_filter': '0.2',
        'descrambler': True,
        # Translators, used as coverage area of a transponder
        'coverage': _('North and South America'),
    }),
]

KU_PRESETS = [
    Preset('Galaxy 19 (97.0W)', 1, {
        'frequency': '11929',
        'symbolrate': '22000',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North America'),
    }),
    Preset('Hotbird 13 (13.0E)', 2, {
        'frequency': '11471',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('Europe, North Africa'),
    }),
    Preset('Intelsat 20 (68.5E)', 3, {
        'frequency': '12522',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North and West Europe, Subsaharan Africa'),
    }),
    Preset('AsiaSat 5 C-band (100.5E)', 4, {
        'frequency': '3960',
        'symbolrate': '30000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('Middle East, Asia, Australia'),
    }),
    Preset('Eutelsat (113.0W)', 5, {
        'frequency': '12089',
        'symbolrate': '11719',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North, Middle, and South America'),
    }),
    Preset('ABS-2 (74.9E)', 6, {
        'frequency': '11734',
        'symbolrate': '44000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('India'),
    }),
]

PRESETS = {
    LBAND: L_PRESETS,
    KUBAND: KU_PRESETS,
}


class DemodRestartError(Exception):
    """ Raised when demodulator cannot be restarted """
    pass


def get_band():
    """
    Return the tuner band for which the application is configured
    """
    return exts.config.get('ondd.band', KUBAND)


def read_ondd_setup():
    settings_key = SETTINGS_KEYS[get_band()]
    initial_data = exts.setup.get(settings_key)
    return {} if isinstance(initial_data, bool) else initial_data


def write_ondd_setup(data):
    settings_key = SETTINGS_KEYS[get_band()]
    exts.setup.append({settings_key: data})


def restart_demod():
    restart_demod_command = exts.config.get('ondd.demod_restart_command')
    try:
        subprocess.check_call(restart_demod_command, shell=True)
    except subprocess.CalledProcessError:
        logging.exception('Failed to restart the demodulator')
        raise DemodRestartError('Could not restart the demod service')


@template_helper()
def has_tuner():
    if get_band() == LBAND:
        return True
    TUNER_DEV_PATH = '/dev/dvb/adapter0/frontend0'
    return os.path.exists(TUNER_DEV_PATH)
