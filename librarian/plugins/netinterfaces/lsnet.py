"""
lsnet.py: Tool for retrieving all network interfaces, based on:
  http://programmaticallyspeaking.com/getting-network-interfaces-in-python.html

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from socket import AF_INET, AF_INET6, inet_ntop
from ctypes import (Structure,
                    Union,
                    POINTER,
                    pointer,
                    get_errno,
                    cast,
                    c_ushort,
                    c_byte,
                    c_void_p,
                    c_char_p,
                    c_uint,
                    c_uint16,
                    c_uint32)
import ctypes.util


class struct_sockaddr(Structure):
    _fields_ = [
        ('sa_family', c_ushort),
        ('sa_data', c_byte * 14),
    ]


class struct_sockaddr_in(Structure):
    _fields_ = [
        ('sin_family', c_ushort),
        ('sin_port', c_uint16),
        ('sin_addr', c_byte * 4),
    ]


class struct_sockaddr_in6(Structure):
    _fields_ = [
        ('sin6_family', c_ushort),
        ('sin6_port', c_uint16),
        ('sin6_flowinfo', c_uint32),
        ('sin6_addr', c_byte * 16),
        ('sin6_scope_id', c_uint32),
    ]


class union_ifa_ifu(Union):
    _fields_ = [
        ('ifu_broadaddr', POINTER(struct_sockaddr)),
        ('ifu_dstaddr', POINTER(struct_sockaddr)),
    ]


class struct_ifaddrs(Structure):
    pass

struct_ifaddrs._fields_ = [
    ('ifa_next', POINTER(struct_ifaddrs)),
    ('ifa_name', c_char_p),
    ('ifa_flags', c_uint),
    ('ifa_addr', POINTER(struct_sockaddr)),
    ('ifa_netmask', POINTER(struct_sockaddr)),
    ('ifa_ifu', union_ifa_ifu),
    ('ifa_data', c_void_p),
]


libc = ctypes.CDLL(ctypes.util.find_library('c'))


def ifap_iter(ifap):
    ifa = ifap.contents
    while True:
        yield ifa
        if not ifa.ifa_next:
            break
        ifa = ifa.ifa_next.contents


def getfamaddr(sa):
    family = sa.sa_family
    addr = None
    if family == AF_INET:
        sa = cast(pointer(sa), POINTER(struct_sockaddr_in)).contents
        addr = inet_ntop(family, sa.sin_addr)
    elif family == AF_INET6:
        sa = cast(pointer(sa), POINTER(struct_sockaddr_in6)).contents
        addr = inet_ntop(family, sa.sin6_addr)
    return family, addr


class NetworkInterface(object):

    def __init__(self, name):
        self.name = name
        self.index = libc.if_nametoindex(name)
        self.addresses = {}

    @property
    def ipv4(self):
        return self.addresses.get(AF_INET)

    @property
    def ipv6(self):
        return self.addresses.get(AF_INET6)


def get_network_interfaces():
    ifap = POINTER(struct_ifaddrs)()
    result = libc.getifaddrs(pointer(ifap))
    if result != 0:
        raise OSError(get_errno())
    del result
    try:
        retval = {}
        for ifa in ifap_iter(ifap):
            name = ifa.ifa_name
            i = retval.get(name)
            if not i:
                i = retval[name] = NetworkInterface(name)
            family, addr = getfamaddr(ifa.ifa_addr.contents)
            if addr:
                i.addresses[family] = addr
        return retval.values()
    finally:
        libc.freeifaddrs(ifap)
