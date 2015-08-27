"""
netutils.py: Network utilities

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request


def get_target_host():
    try:
        host, _ = request.urlparts.netloc.split(':')
    except ValueError:
        host = request.urlparts.netloc

    return host


class IPv4Range(object):

    def __init__(self, start, end, netmask=24):
        self.start = self._parse_ip(start)
        self.end = self._parse_ip(end)
        self.netmask = self._calc_netmask(netmask)

    def __contains__(self, ip):
        parsed = self._parse_ip(ip)
        for start_c, end_c, test_c in zip(self.start, self.end, parsed):
            if start_c == end_c and test_c != start_c:
                return False
            elif test_c not in range(start_c, end_c + 1):
                return False

        return True

    def _parse_ip(self, ip):
        return map(int, ip.split('.'))

    def _calc_netmask(self, netmask):
        expanded = []
        masked = 2 ** (32 - int(netmask))
        while masked > 1:
            expanded.insert(0, max(0, 256 - masked))
            masked /= 256
        return [255] * (4 - len(expanded)) + expanded
