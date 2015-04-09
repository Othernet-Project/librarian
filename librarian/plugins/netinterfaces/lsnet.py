"""
lsnet.py: Tool for retrieving all network interfaces, based on:
  http://programmaticallyspeaking.com/getting-network-interfaces-in-python.html

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import fcntl
import os
import socket
import struct
import ctypes.util


IFF_LOOPBACK = 0x8
SIOCGIWNAME = 0x8B01
SIOCGIFHWADDR = 0x8927

SYSFS_NET_PATH = "/sys/class/net"


class struct_sockaddr(ctypes.Structure):
    _fields_ = [
        ('sa_family', ctypes.c_ushort),
        ('sa_data', ctypes.c_byte * 14),
    ]


class struct_sockaddr_in(ctypes.Structure):
    _fields_ = [
        ('sin_family', ctypes.c_ushort),
        ('sin_port', ctypes.c_uint16),
        ('sin_addr', ctypes.c_byte * 4),
    ]


class struct_sockaddr_in6(ctypes.Structure):
    _fields_ = [
        ('sin6_family', ctypes.c_ushort),
        ('sin6_port', ctypes.c_uint16),
        ('sin6_flowinfo', ctypes.c_uint32),
        ('sin6_addr', ctypes.c_byte * 16),
        ('sin6_scope_id', ctypes.c_uint32),
    ]


class union_ifa_ifu(ctypes.Union):
    _fields_ = [
        ('ifu_broadaddr', ctypes.POINTER(struct_sockaddr)),
        ('ifu_dstaddr', ctypes.POINTER(struct_sockaddr)),
    ]


class struct_ifaddrs(ctypes.Structure):
    pass

struct_ifaddrs._fields_ = [
    ('ifa_next', ctypes.POINTER(struct_ifaddrs)),
    ('ifa_name', ctypes.c_char_p),
    ('ifa_flags', ctypes.c_uint),
    ('ifa_addr', ctypes.POINTER(struct_sockaddr)),
    ('ifa_netmask', ctypes.POINTER(struct_sockaddr)),
    ('ifa_ifu', union_ifa_ifu),
    ('ifa_data', ctypes.c_void_p),
]


libc = ctypes.CDLL(ctypes.util.find_library('c'))


def ifap_iter(ifap):
    ifa = ifap.contents
    while True:
        yield ifa
        if not ifa.ifa_next:
            break
        ifa = ifa.ifa_next.contents


def get_mac_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(),
                       SIOCGIFHWADDR,
                       struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])


def getfamaddr(sa):
    family = sa.sa_family
    addr = None
    if family == socket.AF_INET:
        sa = ctypes.cast(ctypes.pointer(sa),
                         ctypes.POINTER(struct_sockaddr_in)).contents
        addr = socket.inet_ntop(family, sa.sin_addr)
    elif family == socket.AF_INET6:
        sa = ctypes.cast(ctypes.pointer(sa),
                         ctypes.POINTER(struct_sockaddr_in6)).contents
        addr = socket.inet_ntop(family, sa.sin6_addr)
    return family, addr


class NetworkInterface(object):

    def __init__(self, name, mac_addr, is_physical, is_wireless, is_loopback):
        self.name = name
        self.index = libc.if_nametoindex(name)
        self.mac_address = mac_addr
        self.is_physical = is_physical
        self.is_wireless = is_wireless
        self.is_loopback = is_loopback
        self.addresses = {}

    def __setattr__(self, name, value):
        if name == 'ipv4':
            self.addresses[socket.AF_INET] = value
        elif name == 'ipv6':
            self.addresses[socket.AF_INET6] = value
        else:
            super(NetworkInterface, self).__setattr__(name, value)

    @property
    def ipv4(self):
        return self.addresses.get(socket.AF_INET)

    @property
    def ipv6(self):
        return self.addresses.get(socket.AF_INET6)

    @property
    def is_ethernet(self):
        return not self.is_loopback and not self.is_wireless


def is_wireless_interface(ifname):
    path = os.path.join(SYSFS_NET_PATH, ifname, "wireless")
    return os.path.exists(path)


def is_loopback_interface(ifa_flags):
    return bool(ifa_flags & IFF_LOOPBACK)


def is_physical_interface(ifname):
    return os.path.exists(os.path.join(SYSFS_NET_PATH, ifname, "device"))


def get_network_interfaces():
    ifap = ctypes.POINTER(struct_ifaddrs)()
    result = libc.getifaddrs(ctypes.pointer(ifap))
    if result != 0:
        raise OSError(ctypes.get_errno())
    del result
    try:
        retval = {}
        for ifa in ifap_iter(ifap):
            name = ifa.ifa_name
            mac_address = get_mac_address(name)
            is_physical = is_physical_interface(name)
            is_wireless = is_wireless_interface(name)
            is_loopback = is_loopback_interface(ifa.ifa_flags)
            i = retval.get(name)
            if not i:
                i = retval[name] = NetworkInterface(name,
                                                    mac_address,
                                                    is_physical,
                                                    is_wireless,
                                                    is_loopback)
            family, addr = getfamaddr(ifa.ifa_addr.contents)
            if addr:
                i.addresses[family] = addr
        return retval.values()
    finally:
        libc.freeifaddrs(ifap)
