import mock

import gevent.monkey
gevent.monkey.patch_all(aggressive=True)

from librarian.lib import gspawn as mod


MOD = mod.__name__


def test_spawn_calls():
    """ Spawning will call the callable """
    fn = mock.Mock()
    mod.call(fn)
    assert fn.called


def test_spawn_passes_arguments():
    """ Arguments are passed to the callable """
    fn = mock.Mock()
    mod.call(fn, 'foo')
    fn.assert_called_once_with('foo')


def test_spawn_passes_kwargs():
    """ Keyword arguments are passed to the callable """
    fn = mock.Mock()
    mod.call(fn, foo='bar')
    fn.assert_called_once_with(foo='bar')


def test_spawn_returns_callable_return_value():
    """ Return value of the callable is returned by spawn """
    fn = mock.Mock()
    ret = mod.call(fn)
    assert ret == fn.return_value


def test_exception_propagates():
    """ Exceptions raised by the callable are re-raised """
    fn = mock.Mock()
    fn.side_effect = RuntimeError
    try:
        mod.call(fn)
        assert False, 'Expected to raise'
    except RuntimeError:
        pass


def test_with_timeout():
    """ Optional timeout paramter can be used to force a timeout """
    import time
    fn = mock.Mock()
    fn.side_effect = lambda: time.sleep(2)
    try:
        mod.call(fn, _timeout=0.1)
        assert False, 'Expected to raise'
    except mod.TimeoutError:
        pass

