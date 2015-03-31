import socket
import xml.etree.ElementTree as ET

import mock

from librarian.plugins.ondd import ipc as mod


MOD = mod.__name__


def test_read_timeout():
    mocked_socket = mock.Mock()
    mocked_socket.recv.side_effect = mod.socket.timeout

    try:
        mod.read(mocked_socket)
        assert False, 'Timeout was expected'
    except socket.timeout:
        pass


@mock.patch(MOD + '.open_socket')
def test_send_timeout(open_socket):
    mocked_socket = mock.Mock()
    mocked_socket.send.side_effect = mod.socket.timeout
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_socket
    open_socket.return_value = ctx_manager

    result = mod.send('some data')
    assert result is None


@mock.patch(MOD + '.open_socket')
def test_send_success(open_socket):
    data = '<xml />'

    def mocked_recv(size):
        if hasattr(mocked_recv, 'called'):
            return '\0'

        mocked_recv.called = True
        return data

    mocked_socket = mock.Mock()
    mocked_socket.recv.side_effect = mocked_recv
    ctx_manager = mock.MagicMock()
    ctx_manager.__enter__.return_value = mocked_socket
    open_socket.return_value = ctx_manager

    result = mod.send(data)
    assert ET.tostring(result) == data


def test_read_success():
    data = 'something'

    def mocked_recv(size):
        if hasattr(mocked_recv, 'called'):
            return '\0'

        mocked_recv.called = True
        return data

    mocked_socket = mock.Mock()
    mocked_socket.recv.side_effect = mocked_recv

    result = mod.read(mocked_socket)
    assert result == data

