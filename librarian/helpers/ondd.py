import os

from bottle_utils.i18n import lazy_gettext as _

import ondd_ipc.consts as ondd_consts

from ..core.contrib.templates.decorators import template_helper
from ..core.exts import ext_container as exts


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

PRESETS = [
    ('Galaxy 19 (97.0W)', 1, {
        'frequency': '11929',
        'symbolrate': '22000',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North America'),
    }),
    ('Hotbird 13 (13.0E)', 2, {
        'frequency': '11471',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('Europe, North Africa'),
    }),
    ('Intelsat 20 (68.5E)', 3, {
        'frequency': '12522',
        'symbolrate': '27500',
        'polarization': 'v',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North and West Europe, Subsaharan Africa'),
    }),
    ('AsiaSat 5 C-band (100.5E)', 4, {
        'frequency': '3960',
        'symbolrate': '30000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('Middle East, Asia, Australia'),
    }),
    ('Eutelsat (113.0W)', 5, {
        'frequency': '12089',
        'symbolrate': '11719',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('North, Middle, and South America'),
    }),
    ('ABS-2 (74.9E)', 6, {
        'frequency': '11734',
        'symbolrate': '44000',
        'polarization': 'h',
        'delivery': 'DVB-S',
        'modulation': 'QPSK',
        # Translators, used as coverage area of a transponder
        'coverage': _('India'),
    }),
]


def read_ondd_setup():
    initial_data = exts.setup.get('ondd')
    return {} if isinstance(initial_data, bool) else initial_data


@template_helper()
def has_tuner():
    TUNER_DEV_PATH = '/dev/dvb/adapter0/frontend0'
    return os.path.exists(TUNER_DEV_PATH)
