import multiprocessing
import os
import socket
import time
import xml.etree.ElementTree as ET

import mock


SOCK_FILE_PATH = '/tmp/test_server.sock'


def get_config(key):
    config = {'ondd.socket': SOCK_FILE_PATH,
              'ondd.timeout': 1}
    return config[key]


class TestServer(multiprocessing.Process):

    def __init__(self, socket_file_path, delay=0, response=None):
        multiprocessing.Process.__init__(self)

        self._response = response
        self._delay = delay
        self._socket_file_path = socket_file_path
        if os.path.exists(self._socket_file_path):
            os.remove(self._socket_file_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self._socket_file_path)
        self.server.listen(5)
        self.server.setblocking(0)
        self.exit = multiprocessing.Event()

    def run(self):
        while not self.exit.is_set():
            time.sleep(self._delay)
            conn, addr = self.server.accept()
            while not self.exit.is_set():
                data = conn.recv(1024)
                if not data:
                    break
                else:
                    conn.send(self._response or data)

    def shutdown(self):
        self.exit.set()
        self.server.close()
        os.remove(self._socket_file_path)


@mock.patch('bottle.request')
def test_read_timeout(bottle_request):
    from librarian.plugins.ondd import ipc

    test_server = TestServer(SOCK_FILE_PATH, delay=2)
    test_server.start()

    bottle_request.app.config.__getitem__.side_effect = get_config

    sock = ipc.connect(SOCK_FILE_PATH)

    try:
        ipc.read(sock)
        assert False, 'Timeout was expected'
    except socket.timeout:
        pass

    test_server.shutdown()
    test_server.join()


@mock.patch('bottle.request')
def test_send_timeout(bottle_request):
    from librarian.plugins.ondd import ipc

    test_server = TestServer(SOCK_FILE_PATH, delay=2)
    test_server.start()

    bottle_request.app.config.__getitem__.side_effect = get_config

    result = ipc.send('some data')
    assert result is None

    test_server.shutdown()
    test_server.join()


@mock.patch('bottle.request')
def test_send_success(bottle_request):
    from librarian.plugins.ondd import ipc

    test_server = TestServer(SOCK_FILE_PATH)
    test_server.start()

    bottle_request.app.config.__getitem__.side_effect = get_config

    response = ipc.send('<xml />')
    assert ET.tostring(response) == '<xml />'

    test_server.shutdown()
    test_server.join()


@mock.patch('bottle.request')
def test_read_success(bottle_request):
    from librarian.plugins.ondd import ipc

    test_server = TestServer(SOCK_FILE_PATH, response='test data\0')
    test_server.start()

    bottle_request.app.config.__getitem__.side_effect = get_config

    sock = ipc.connect(SOCK_FILE_PATH)
    sock.send('ignored')
    response = ipc.read(sock)

    assert response == 'test data'

    test_server.shutdown()
    test_server.join()
