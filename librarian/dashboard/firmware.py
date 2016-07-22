"""
Dashboard plugin that presents a UI for updating the device firmware

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from ..forms.firmware import FirmwareUpdateForm
from ..presentation.dashboard.dashboard import DashboardPlugin


class FirmwareUpdateDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Update Firmware')
    name = 'firmware'

    def get_template(self):
        return self.name + '/dashboard.tpl'

    def get_context(self):
        form = FirmwareUpdateForm()
        return dict(form=form)
