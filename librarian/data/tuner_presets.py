from collections import namedtuple

from bottle_utils.i18n import lazy_gettext as _


__all__ = ('LBAND', 'KUBAND', 'L_PRESETS', 'KU_PRESETS', 'PRESETS')


Preset = namedtuple('Preset', ('label', 'index', 'values'))

LBAND = 'l'
KUBAND = 'ku'

L_PRESETS = [
    # Translators, name of the L-band tuner preset covering AF-EU-ME
    Preset(_('Africa-Europe-Middle East (25E)'), 1, {
        'frequency': '1545.94',
        'uncertainty': '4000',
        'symbolrate': '4200',
        'sample_rate': '1',
        'rf_filter': '20',
        'descrambler': True,
        # Translators, used as coverage area of a transponder
        'coverage': _('Africa, Europe, Middle East'),
    }),
    # Translators, name of the L-band tuner preset covering the Americas
    Preset(_('North and South America (98W)'), 2, {
        'frequency': '1539.8725',
        'uncertainty': '4000',
        'symbolrate': '4200',
        'sample_rate': '1',
        'rf_filter': '20',
        'descrambler': True,
        # Translators, used as coverage area of a transponder
        'coverage': _('North and South America'),
    }),
    # Translators, name of the L-band tuner preset covering Asia-Pacific
    Preset(_('Asia-Pacific (144E)'), 3, {
        'frequency': '1545.9525',
        'uncertainty': '4000',
        'symbolrate': '4200',
        'sample_rate': '1',
        'rf_filter': '20',
        'descrambler': True,
        # Translators, used as coverage area of a transponder
        'coverage': _('Asia, Oceania'),
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
