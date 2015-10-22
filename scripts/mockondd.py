"""
mockondd.py: Quick and dirty ONDD mock

IPC calls mocked:
/status
/transfers
/settings

"""

from __future__ import print_function

from gevent import monkey
monkey.patch_all(thread=False, aggressive=True)

import os
import re
import argparse
import random
import socket
from contextlib import contextmanager
from functools import wraps

from gevent.server import StreamServer


SOCKET_PATH = '/tmp/ondd.ctrl'
IN_ENCODING = 'ascii'
OUT_ENCODING = 'ascii'


def prepare_socket(path):
    try:
        os.unlink(path)
    except OSError:
        if(os.path.exists(path)):
            raise
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(path)
    sock.listen(1)
    return sock


@contextmanager
def open_socket(path):
    sock = prepare_socket(path)
    try:
        yield sock
    finally:
        sock.close()


def read_request(sock, buff_size=2048):
    data = buff = sock.recv(buff_size)
    while buff and '\0' not in buff:
        buff = sock.recv(buff_size)
        data += buff
    return data[:-1].decode(IN_ENCODING)


def rand_fname():
    return 'files/file-%s.txt' % str(random.randrange(1, 100))


def rand_hash():
    return "%032x" % random.getrandbits(128)

EMPTY_TRANSFER = """
    <transfer>
          <carousel_id>1</carousel_id>
          <path></path>
          <hash></hash>
          <block_count>0</block_count>
          <block_received>0</block_received>
          <complete></complete>
    </transfer>
    """

def rand_transfer():
    random_data = """
    <transfer>
          <carousel_id>1</carousel_id>
          <path>%s</path>
          <hash>%s</hash>
          <block_count>%d</block_count>
          <block_received>%d</block_received>
          <complete>%s</complete>
    </transfer>
    """ % (rand_fname(), rand_hash(), random.randrange(4000, 5000),
           random.randrange(1, 4000), random.choice(['yes', 'no']))
    return random.choice([random_data, random_data, random_data,
                          EMPTY_TRANSFER])


def sender(fn):
    @wraps(fn)
    def wrapper(sock, debug=False):
        res = fn()
        if debug:
            print('===>', res)
        sock.sendall(res + '\0')
        sock.close()
    return wrapper


@sender
def send_transfers_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<response code="200">
  <streams>
    <stream>
      <pid>65</pid>
      <transfers>
      %s
      %s
      %s
      </transfers>
    </stream>
  </streams>
</response>""" % (rand_transfer(), rand_transfer(), rand_transfer())


@sender
def send_status_response():
    snr = round(random.randrange(0, 16) / 10.0, 2)
    signal = random.randrange(0, 100)
    bitrate = random.randrange(15000, 93400)
    lock = random.choice(('yes', 'yes', 'yes', 'yes', 'no'))
    return """<?xml version="1.0" encoding="UTF-8"?>
<response code="200">
    <tuner>
        <lock>{lock}</lock>
        <signal>{signal}</signal>
        <snr>{snr}</snr>
    </tuner>
    <streams>
        <stream>
            <pid>65</pid>
            <bitrate>{bitrate}</bitrate>
            <ident>outernet-0</ident>
        </stream>
    </streams>
</response>""".format(lock=lock, signal=signal, snr=snr, bitrate=bitrate)


@sender
def send_settings_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<response code="200">
    <tuner>
        <delivery>DVB-S</delivery>
        <modulation>QPSK</modulation>
        <frequency>1577</frequency>
        <symbolrate>23000</symbolrate>
        <voltage>13</voltage>
        <tone>yes</tone>
        <azimuth/>
    </tuner>
</response>"""


@sender
def send_default_response():
    return """<?xml version="1.0" encoding="UTF-8"?>
<response code="204"/>
"""


ENDPOINT_MAPPING = (
    (re.compile('<get.*status.*'), send_status_response),
    (re.compile('<get.*transfers.*'), send_transfers_response),
    (re.compile('<get.*settings.*'), send_settings_response),
    (re.compile('.*'), send_default_response), # catch-all
)


def get_handler(debug=False):
    def request_handler(sock, address):
        request = read_request(sock)
        if debug:
            print('<===', request)
        for rxp, refn in ENDPOINT_MAPPING:
            if not rxp.match(request):
                continue
            refn(sock, debug)
    return request_handler


def main():
    parser = argparse.ArgumentParser(description='Mock ONDD')
    parser.add_argument('--socket', metavar='PATH',
                        help='Path to socket',
                        default=SOCKET_PATH)
    parser.add_argument('--verbose', action='store_true',
                        help='Print out requests and responses')
    args = parser.parse_args()

    with open_socket(args.socket) as sock:
        server = StreamServer(sock, get_handler(args.verbose))
        server.serve_forever()


if __name__ == "__main__":
    main()
