"""
plugin.py: ONDD plugin

Allows Librarian to communicate with ONDD.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from ..forms import ondd as ondd_forms
from ..helpers import ondd as ondd_helpers
from ..core.contrib.templates.decorators import template_helper
from ..presentation.dashboard.dashboard import DashboardPlugin


COMPARE_KEYS = ('frequency', 'symbolrate', 'polarization', 'delivery',
                'modulation')


@template_helper()
def get_bitrate(status):
    for stream in status.get('streams', []):
        return stream['bitrate']

    return 0


def get_presets():
    return ondd_helpers.PRESETS[ondd_helpers.get_band()]


def match_preset(data):
    presets = get_presets()
    if not data:
        return 0
    data = {k: str(v) for k, v in data.items() if k in COMPARE_KEYS}
    for preset in presets:
        preset_data = {k: v for k, v in preset[2].items() if k in COMPARE_KEYS}
        if preset_data == data:
            return preset[1]
    return -1


class ONDDDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Tuner settings')
    name = 'ondd'
    priority = 10

    def get_template(self):
        return 'ondd/dashboard'

    def get_context(self):
        initial_data = ondd_helpers.read_ondd_setup()
        preset = match_preset(initial_data)
        ONDDForm = ondd_forms.FORMS[ondd_helpers.get_band()]
        band = ondd_helpers.get_band()
        return dict(band=band,
                    lband=ondd_helpers.LBAND,
                    kuband=ondd_helpers.KUBAND,
                    is_l=band == ondd_helpers.LBAND,
                    is_ku=band == ondd_helpers.KUBAND,
                    preset_keys=ONDDForm.PRESETS[0].values.keys(),
                    form=ONDDForm(initial_data),
                    selected_preset=preset)
