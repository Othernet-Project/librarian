"""
plugin.py: Network interfaces plugin

Display all available network interfaces on device.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils.i18n import lazy_gettext as _

from ..dashboard import DashboardPlugin

from .lsnet import get_network_interfaces


def install(app, route):
    pass


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Network interfaces')
    name = 'netinterfaces'

    def get_context(self):
        all_interfaces = get_network_interfaces()
        physicals = dict((i.mac_address, i)
                         for i in all_interfaces if i.is_physical)
        # if physical interface is bridged, it will have no ip addresses
        # assigned to it directly
        for virtual in (i for i in all_interfaces if not i.is_physical):
            iface = physicals.get(virtual.mac_address)
            if iface:
                iface.ipv4 = iface.ipv4 or virtual.ipv4
                iface.ipv6 = iface.ipv6 or virtual.ipv6

        return dict(interfaces=physicals.values())
