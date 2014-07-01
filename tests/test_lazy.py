from unittest import mock

from librarian.lazy import *


def get_lazy(*args, **kwargs):
    fn = mock.Mock()
    lazy = Lazy(fn, *args, **kwargs)
    assert fn.call_count == 0, "Fresh lazy object, should not have eval'd"
    return fn, lazy


def test_eval():
    """ Creates basic Lazy object """
    fn, lazy = get_lazy(1, 2)
    lazy._eval()
    fn.assert_called_once_with(1, 2)


def test_kwarg():
    """ Should also work with keyword arguments """
    fn, lazy = get_lazy(foo='bar')
    lazy._eval()
    fn.assert_called_once_with(foo='bar')


def test_return():
    """ Returns function's return value """
    fn, lazy = get_lazy()
    ret = lazy._eval()
    assert ret == fn.return_value, "Should return function's return value"


def test_coerced():
    """ Should evaluate a function when coerced with string """
    fn, lazy = get_lazy()
    fn.return_value = 'foo'
    s = lazy + 'bar'
    assert s == 'foobar', "Should be 'foobar', got '%s'" % s


def test_interpolated():
    """ Should evaluate a function when interpolated into string """
    fn, lazy = get_lazy()
    fn.return_value = 'foo'
    s = '%sbar' % lazy
    assert s == 'foobar', "Should be 'foobar', got '%s'" % s


def test_formatted():
    """ Should evaluate a function when string-formatted """
    fn, lazy = get_lazy()
    fn.return_value = 'foo'
    s = '{}bar'.format(lazy)
    assert s == 'foobar', "Should be 'foobar', got '%s'" % s


def test_boolean_coercion():
    """ Boolean coercion should work lazily """
    fn, lazy = get_lazy()
    bool(lazy)
    assert fn.called_once(), "Should be called once"


def test_comparison():
    """ Function should be called when being compared to other values """
    fn, lazy = get_lazy()
    fn.return_value = 1
    assert lazy < 2
    assert lazy > 0
    assert lazy == 1
    assert lazy >= 1
    assert lazy <= 1
    assert lazy != 0
    assert fn.called_once(), "Expected one cal, got %s" % fn.call_count


def test_calling():
    """ Calling the lazy object will call function's return value """
    fn, lazy = get_lazy()
    lazy()
    assert fn.return_value.called_once(), "Should have called return value"


def test_decorator():
    """ Test lazy decorator """
    fn = mock.Mock()
    lazy_fn = lazy(fn)
    val = lazy_fn()
    assert fn.called == False, "Should not be called before value is accessed"
    assert isinstance(val, Lazy), "Return value should be a Lazy instance"

