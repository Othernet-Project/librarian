import os
import time
import socket
import functools
import multiprocessing
import xml.etree.ElementTree as ET

import mock


SOCK_FILE_PATH = '/tmp/test_server.sock'


def if_supported(fn):
    """ Only run function if socket support is available """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if hasattr(socket, 'AF_UNIX'):
            return fn(*args, **kwargs)
    return wrapper



def get_config(key):
    config = {'ondd.socket': SOCK_FILE_PATH}
    return config[key]


class TestServer(multiprocessing.Process):

    def __init__(self, socket_file_path, delay=0, response=None, is_blocking=1):  # NOQA
        multiprocessing.Process.__init__(self)

        self._response = response
        self._delay = delay
        self._socket_file_path = socket_file_path
        if os.path.exists(self._socket_file_path):
            os.remove(self._socket_file_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self._socket_file_path)
        self.server.listen(5)
        self.server.setblocking(is_blocking)
        self.started = multiprocessing.Event()
        self.exit = multiprocessing.Event()

    def run(self):
        while not self.exit.is_set():
            time.sleep(self._delay)
            self.started.set()
            conn, addr = self.server.accept()
            if self._response:
                conn.send(self._response)
            else:
                data = conn.recv(1024)
                if not data:
                    break
                else:
                    conn.send(self._response or data)
            conn.close()

    def shutdown(self):
        self.exit.set()
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        os.remove(self._socket_file_path)

    def wait_until_started(self):
        while not self.started.is_set():
            time.sleep(0.1)


def patch_ipc(func):
    def _patch_ipc(*args, **kwargs):
        from librarian.plugins.ondd import ipc

        original_timeout = ipc.ONDD_SOCKET_TIMEOUT
        setattr(ipc, 'ONDD_SOCKET_TIMEOUT', 1)

        result = func(ipc, *args, **kwargs)

        setattr(ipc, 'ONDD_SOCKET_TIMEOUT', original_timeout)

        return result
    return _patch_ipc


@if_supported
@mock.patch('bottle.request')
@patch_ipc
def test_read_timeout(ipc, bottle_request):
    test_server = TestServer(SOCK_FILE_PATH, delay=2, is_blocking=0)
    test_server.start()
    test_server.wait_until_started()

    bottle_request.app.config.__getitem__.side_effect = get_config

    sock = ipc.connect(SOCK_FILE_PATH)

    try:
        ipc.read(sock)
        assert False, 'Timeout was expected'
    except socket.timeout:
        pass

    test_server.shutdown()
    test_server.join()


@if_supported
@mock.patch('bottle.request')
@patch_ipc
def test_send_timeout(ipc, bottle_request):
    test_server = TestServer(SOCK_FILE_PATH, delay=2, is_blocking=0)
    test_server.start()
    test_server.wait_until_started()

    bottle_request.app.config.__getitem__.side_effect = get_config

    result = ipc.send('some data')
    assert result is None

    test_server.shutdown()
    test_server.join()


@if_supported
@mock.patch('bottle.request')
@patch_ipc
def test_send_success(ipc, bottle_request):
    test_server = TestServer(SOCK_FILE_PATH)
    test_server.start()
    test_server.wait_until_started()

    bottle_request.app.config.__getitem__.side_effect = get_config

    response = ipc.send('<xml />')
    assert ET.tostring(response) == '<xml />'

    test_server.shutdown()
    test_server.join()


@if_supported
@mock.patch('bottle.request')
@patch_ipc
def test_read_success(ipc, bottle_request):
    test_server = TestServer(SOCK_FILE_PATH, response='test data\0')
    test_server.start()
    test_server.wait_until_started()

    bottle_request.app.config.__getitem__.side_effect = get_config

    sock = ipc.connect(SOCK_FILE_PATH)
    response = ipc.read(sock)

    assert response == 'test data'

    test_server.shutdown()
    test_server.join()
