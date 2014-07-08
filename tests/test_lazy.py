"""
test_lazy.py: Unit tests for ``librarian.lazy`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


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


def test_reverse_coerced():
    """ Should evaluate a function when added to a string """
    fn, lazy = get_lazy()
    fn.return_value = 'foo'
    s = 'bar' + lazy
    assert s == 'barfoo'
    s = 'bar'
    s += lazy
    assert s == 'barfoo'


def test_coercion_should_return_string():
    fn, lazy = get_lazy()
    fn.return_value = 1
    try:
        s = str(lazy)
    except Exception as err:
        assert False, "Should not raise, but raised '%s'" % err
    assert s == '1', "S should be string '1', got '%s' instead" % s


def test_coercion_into_bytes():
    fn, lazy = get_lazy()
    fn.return_value = 1
    try:
        s = bytes(lazy)
    except Exception as err:
        assert False, "Should not raise, but raised '%s'" % err
    assert s == b'\x00', "Should be b'\x00', got '%s' instead" % s


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
    fn.assert_called_once()


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
    assert fn.call_count == 6, "Expected 6 calls, got %s" % fn.call_count


def test_call():
    """ Calling the lazy object """
    fn, lazy = get_lazy()
    lazy()
    fn.return_value.assert_called_once()


def test_caching():
    """ Caching lazy only evaluates once """
    fn = mock.Mock()
    lazy = CachingLazy(fn)
    lazy._eval()
    lazy._eval()
    assert fn.call_count == 1, "Expected one call, got %s" % fn.call_count
    assert lazy._called, "Should set called flag to True"


def test_decorator():
    """ Calling the lazy object will call function's return value """
    fn = mock.Mock()
    lazy_fn = lazy(fn)
    val = lazy_fn()
    assert fn.called == False, "Should not be called before value is accessed"
    assert isinstance(val, Lazy), "Return value should be a Lazy instance"


def test_caching_vs_noncaching():
    """ Testing use of different Lazy classes """
    fn1 = mock.Mock()
    fn2 = mock.Mock()
    lazy_fn = lazy(fn1)
    lazy_caching_fn = lazy(fn2, CachingLazy)
    val1 = lazy_fn()
    val1._eval()
    val1._eval()
    val1._eval()
    val2 = lazy_caching_fn()
    val2._eval()
    val2._eval()
    val2._eval()
    assert fn1.call_count == 3, "Expected 3 calls, got %s" % fn1.call_count
    assert fn2.call_count == 1, "Expected one call, got %s" % fn2.call_count
    assert isinstance(val1, Lazy), "Expected Lazy instance"
    assert isinstance(val2, CachingLazy), "Expected CachingLazy instance"


def test_decorator_with_args():
    fn = mock.Mock()
    fn.return_value = 'foo'
    lazy_fn = lazy(fn)
    lazy_fn(1, 2, 3)._eval()
    fn.assert_called_once_with(1, 2, 3)


def test_decorator_with_kwargs():
    fn = mock.Mock()
    fn.return_value = 'foo'
    lazy_fn = lazy(fn)
    lazy_fn(1, 2, foo=3)._eval()
    fn.assert_called_once_with(1, 2, foo=3)


def test_lazy_class():
    fn = mock.Mock()
    fn.return_value = 1  # int
    lazy_fn = lazy(fn)
    lazy_obj = lazy_fn()
    assert isinstance(lazy_obj, int)
    fn.return_value = 'str'  # str
    assert isinstance(lazy_obj, str)


def test_subscript():
    fn = mock.Mock()
    fn.return_value = 'foo'
    lazy_fn = lazy(fn)
    lazy_obj = lazy_fn()
    assert lazy_obj[:2] == 'fo'


def test_methods():
    fn = mock.Mock()
    fn.return_value = 'foobar'
    lazy_fn = lazy(fn)
    lazy_obj = lazy_fn()
    assert lazy_obj.replace('bar', 'foo') == 'foofoo'

