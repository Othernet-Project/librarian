"""
plugin.py: Network interfaces plugin

Display all available network interfaces on device.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from collections import namedtuple

from bottle import request
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
        interfaces = [iface for iface in get_network_interfaces()
                      if not iface.is_loopback]
        # sorted_interfaces = sorted(interfaces, key=lambda x: x.index)
        # TODO: replace this workaround with a proper solution when the bug in
        # lsnet.py is fixed that's causing the `ioctl` call to fail.
        conf = request.app.config
        ethernet_interfaces = conf.get('netinterfaces.wired', [])
        wireless_interfaces = conf.get('netinterfaces.wireless', [])
        matched_interfaces = []

        Interface = namedtuple('Interface', ['name',
                                             'ipv4',
                                             'ipv6',
                                             'is_ethernet',
                                             'is_wireless',
                                             'is_loopback'])
        for iface in (i for i in interfaces if i.name in ethernet_interfaces):
            matched_interfaces.append(Interface(name=iface.name,
                                                ipv4=iface.ipv4,
                                                ipv6=iface.ipv6,
                                                is_ethernet=True,
                                                is_wireless=False,
                                                is_loopback=False))

        for iface in (i for i in interfaces if i.name in wireless_interfaces):
            matched_interfaces.append(Interface(name=iface.name,
                                                ipv4=iface.ipv4,
                                                ipv6=iface.ipv6,
                                                is_ethernet=False,
                                                is_wireless=True,
                                                is_loopback=False))

        return dict(interfaces=matched_interfaces)
