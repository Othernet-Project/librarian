import mock
import pytest

from librarian.core import pubsub as mod


@pytest.fixture
def pubsub():
    return mod.PubSub()


def test_publish_no_listeners(pubsub):
    try:
        pubsub.publish('myevent', 1, 2)
    except Exception:
        pytest.fail('Should not raise.')


def test_publish_has_listeners(pubsub):
    order_checker = mock.Mock()

    first = mock.Mock()
    first.side_effect = lambda *args, **kwargs: order_checker('first')
    second = mock.Mock()
    second.side_effect = lambda *args, **kwargs: order_checker('second')

    pubsub._subscribers['myevent'] = [(first, mod.DEFAULT_CONDITION),
                                      (second, mod.DEFAULT_CONDITION)]
    pubsub.publish('myevent', 1, 2, a='test')

    first.assert_called_once_with(1, 2, a='test')
    second.assert_called_once_with(1, 2, a='test')
    order_checker.assert_has_calls([mock.call('first'), mock.call('second')])


def test_publish_to_scope(pubsub):
    first = mock.MagicMock()
    first.__module__ = 'librarian_first_component.module'

    second = mock.MagicMock()
    second.__module__ = 'librarian_second_component.module'

    pubsub._subscribers['myevent'] = [(first, mod.DEFAULT_CONDITION),
                                      (second, mod.DEFAULT_CONDITION)]
    pubsub._scopes[id(first)] = first.__module__
    pubsub._scopes[id(second)] = second.__module__
    pubsub.publish('myevent',
                   1,
                   2,
                   a='test',
                   scope='librarian_second_component.module')

    assert not first.called
    second.assert_called_once_with(1, 2, a='test')


def test_publish_with_condition(pubsub):
    # can never execute
    first = mock.Mock()
    f_cond = mock.Mock()
    f_cond.side_effect = lambda ev, x: False
    # should always execute
    second = mock.Mock()
    s_cond = mock.Mock()
    s_cond.side_effect = lambda ev, x: True

    pubsub._subscribers['myevent'] = [(first, f_cond), (second, s_cond)]
    pubsub.publish('myevent', 42)
    # check listeners
    assert not first.called
    second.assert_called_once_with(42)
    # check conditions
    f_cond.assert_called_once_with('myevent', 42)
    s_cond.assert_called_once_with('myevent', 42)


def test_subscribe_new(pubsub):
    assert 'test' not in pubsub._subscribers
    first = mock.Mock()
    second = mock.Mock()
    cond = lambda x: True
    pubsub.subscribe('test', first)
    pubsub.subscribe('test', second, condition=cond)
    assert pubsub._subscribers['test'] == [(first, mod.DEFAULT_CONDITION),
                                           (second, cond)]


def test_subscribe_already_exists(pubsub):
    assert 'test' not in pubsub._subscribers
    func = mock.Mock()
    pubsub.subscribe('test', func)
    pubsub.subscribe('test', func)
    assert pubsub._subscribers['test'] == [(func, mod.DEFAULT_CONDITION)]


def test_unsubscribe(pubsub):
    func = mock.Mock()
    pubsub._subscribers['test'] = [(func, None)]
    pubsub._scopes[id(func)] = 'func.path'
    pubsub.unsubscribe('test', func)
    assert pubsub._subscribers['test'] == []
    assert 'test' not in pubsub._scopes


def test_unsubscribe_was_not_subscribed(pubsub):
    func = mock.Mock()
    pubsub._subscribers['test'] = []
    try:
        pubsub.unsubscribe('test', func)
    except Exception:
        pytest.fail('Should not raise.')

    assert pubsub._subscribers['test'] == []


def test_get_subscribers_copies(pubsub):
    func = mock.Mock()
    pubsub._subscribers['test'] = [func]
    listeners = pubsub.get_subscribers('test')
    assert listeners == [func]
    assert listeners is not pubsub._subscribers['test']
    listeners.remove(func)
    assert pubsub._subscribers['test'] == [func]
