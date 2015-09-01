from bottle_utils.i18n import lazy_gettext as _

try:
    from . import ipc
except AttributeError:
    raise RuntimeError('ONDD plugin requires UNIX sockets')


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
