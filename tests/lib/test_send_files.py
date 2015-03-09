import mock

from librarian.lib import send_file


def test_file_range_wrapper_seeks():
    """ File ranger wrapper seeks to start of the range """
    fd = mock.Mock()
    send_file.FileRangeWrapper(fd, offset=2, length=5)
    fd.seek.called_once_with(2)


def test_file_range_wrapper_calls_read_when_no_seek():
    """ Wrapper falls back to reading when seek doesn't work """
    class faux_fd(object):
        read = lambda x: 'foo'
    fd = mock.Mock(spec_set=faux_fd())
    try:
        send_file.FileRangeWrapper(fd, offset=2, length=5)
    except AttributeError:
        assert False, 'Expected not to raise'
    fd.read.assert_called_once_with(2)


def test_file_range_wrapper_read_method():
    """ When read, wrapper reads up to specified length """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    wrapped.read()
    fd.read.assert_called_once_with(5)


def test_file_range_wrapper_read_size():
    """ The read() method takes size argument for custom chunk size """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    wrapped.read(2)
    fd.read.assert_called_once_with(2)


def test_file_range_wrapper_cannot_read_past_length():
    """ The size passed to read() cannot be larger than length """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    wrapped.read(10)
    fd.read.assert_called_once_with(5)


def test_file_range_wrapper_reading_past_length():
    """ Empty string is returned past length mark """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    ret1 = wrapped.read(3)
    ret2 = wrapped.read(3)
    ret3 = wrapped.read(3)
    fd.read.assert_has_calls([mock.call(3), mock.call(2)])
    assert ret1 == fd.read.return_value
    assert ret2 == fd.read.return_value
    assert ret3 == ''


def test_file_range_wrapper_has_close():
    """ It is possible to close the file handle by calling close() """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    wrapped.close()
    assert fd.close.called


def test_file_range_wrapper_value_error_after_close():
    """ Calling read() after close() will raise ValueError """
    fd = mock.Mock()
    wrapped = send_file.FileRangeWrapper(fd, offset=2, length=5)
    wrapped.close()
    try:
        wrapped.read()
        assert False, 'Expected to raise'
    except ValueError:
        pass
