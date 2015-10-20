"""
mockondd.py: Quick and dirty ONDD mock

IPC calls mocked:
/status
/transfers
/settings

"""

from gevent import monkey
monkey.patch_all(thread=False, aggressive=True)

import os
import re
import argparse
import random
import socket

from contextlib import contextmanager

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


status_re = re.compile('.*status.*')
transfers_re = re.compile('.*transfers.*')
settings_re = re.compile('.*settings.*')


def rand_fname():
    return 'files/file-%s.txt' % str(random.randrange(1, 100))


def rand_hash():
    return "%032x" % random.getrandbits(128)


def rand_transfer():
    return """
    <transfer>
          <carousel_id>1</carousel_id>
          <path>%s</path>
          <hash>%s</hash>
          <block_count>%d</block_count>
          <block_received>%d</block_received>
          <complete>%s</complete>
    </transfer>
    """ % (rand_fname(), rand_hash(), random.randrange(4000, 5000), random.randrange(1, 4000), 'yes')


def send_transfers_response(sock):
    response = """<?xml version="1.0" encoding="UTF-8"?>
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
</response>\0""" % (rand_transfer(), rand_transfer(), rand_transfer())
    sock.sendall(response)


def send_status_response(sock):
    response = """<?xml version="1.0" encoding="UTF-8"?>
<response code="200">
    <tuner>
        <lock>yes</lock>
        <signal>65</signal>
        <snr>0.00</snr>
    </tuner>
    <streams>
        <stream>
            <pid>65</pid>
            <bitrate>55355</bitrate>
            <ident>outernet-0</ident>
        </stream>
    </streams>
</response>\0"""
    sock.sendall(response)


def send_settings_response(sock):
    response = """<?xml version="1.0" encoding="UTF-8"?>
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
</response>\0"""
    sock.sendall(response)


def request_handler(sock, address):
    request = read_request(sock)
    if status_re.match(request):
        send_status_response(sock)
    elif transfers_re.match(request):
        send_transfers_response(sock)
    elif settings_re.match(request):
        send_settings_response(sock)
    sock.close()


def main():
    parser = argparse.ArgumentParser(description='Mock ONDD')
    parser.add_argument('--socket', metavar='PATH',
                        help='Path to socket',
                        default=SOCKET_PATH)
    args = parser.parse_args()

    with open_socket(args.socket) as sock:
        server = StreamServer(sock, request_handler)
        server.serve_forever()


if __name__ == "__main__":
    main()
