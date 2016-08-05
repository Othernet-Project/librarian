from ..core.exts import ext_container as exts
from ..data.state.provider import StateProvider


class ONDDProvider(StateProvider):
    name = 'ondd'
    allowed_methods = 'rw'

    def get_default_value(self):
        cache_max = exts.config['ondd.cache_quota']
        return {
            'cache': {
                'total': cache_max,
                'free': cache_max,
                'used': 0,
                'alert': None
            },
            'status': {
                'freq': '0.00',
                'freq_offset': '0.00',
                'set_rs': '0',
                'rssi': '0.00',
                'snr': '0.00',
                'ser': '0.00',
                'crc_ok': '0',
                'crc_err': '0',
                'alg_pk_mn': '0.00',
                'state': '',
                'indicator': '-search'
            },
            'transfers': {},
        }
