import os
import logging
import subprocess
from collections import namedtuple

from bottle_utils.i18n import lazy_gettext as _

import ondd_ipc.consts as ondd_consts

from ..core.exts import ext_container as exts
from ..core.contrib.templates.decorators import template_helper
from ..data.tuner_presets import LBAND, KUBAND, L_PRESETS, KU_PRESETS, PRESETS


#: The key in the application settings JSON file that contains the tuner params
SETTINGS_KEYS = {
    LBAND: 'ondd_l',
    KUBAND: 'ondd'
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
    ('10', '10%'),
    ('20', '20%'),
    ('40', '40%')
)


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
