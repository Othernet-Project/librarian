import socket
import xml.etree.ElementTree as ET

import mock

from librarian.plugins.ondd import ipc as mod


MOD = mod.__name__
SOCK_FILE_PATH = '/tmp/test_server.sock'


def get_config(key):
    config = {'ondd.socket': SOCK_FILE_PATH}
    return config[key]


def test_connect_timeout():
    with mock.patch(MOD + '.socket.socket') as ipc_socket:
        mocked_socket = mock.Mock()
        mocked_socket.connect.side_effect = mod.socket.timeout
        ipc_socket.return_value = mocked_socket

        try:
            mod.connect(SOCK_FILE_PATH)
            assert False, 'Timeout was expected'
        except socket.timeout:
            pass


@mock.patch(MOD + '.request')
def test_read_timeout(bottle_request):
    bottle_request.app.config.__getitem__.side_effect = get_config

    with mock.patch(MOD + '.socket.socket') as ipc_socket:
        mocked_socket = mock.Mock()
        mocked_socket.recv.side_effect = mod.socket.timeout
        ipc_socket.return_value = mocked_socket

        try:
            mod.read(mocked_socket)
            assert False, 'Timeout was expected'
        except socket.timeout:
            pass


@mock.patch(MOD + '.request')
def test_send_timeout(bottle_request):
    bottle_request.app.config.__getitem__.side_effect = get_config

    with mock.patch(MOD + '.socket.socket') as ipc_socket:
        mocked_socket = mock.Mock()
        mocked_socket.send.side_effect = mod.socket.timeout
        ipc_socket.return_value = mocked_socket

        result = mod.send('some data')
        assert result is None


@mock.patch(MOD + '.request')
def test_send_success(bottle_request):
    bottle_request.app.config.__getitem__.side_effect = get_config
    data = '<xml />'

    def mocked_recv(size):
        if hasattr(mocked_recv, 'called'):
            return '\0'

        mocked_recv.called = True
        return data

    with mock.patch(MOD + '.socket.socket') as ipc_socket:
        mocked_socket = mock.Mock()
        mocked_socket.recv.side_effect = mocked_recv
        ipc_socket.return_value = mocked_socket

        result = mod.send(data)
        assert ET.tostring(result) == data


@mock.patch(MOD + '.request')
def test_read_success(bottle_request):
    bottle_request.app.config.__getitem__.side_effect = get_config
    data = 'something'

    def mocked_recv(size):
        if hasattr(mocked_recv, 'called'):
            return '\0'

        mocked_recv.called = True
        return data

    with mock.patch(MOD + '.socket.socket') as ipc_socket:
        mocked_socket = mock.Mock()
        mocked_socket.recv.side_effect = mocked_recv
        ipc_socket.return_value = mocked_socket

        result = mod.read(mocked_socket)
        assert result == data
