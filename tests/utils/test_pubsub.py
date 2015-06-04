import mock
import pytest

from librarian.utils import pubsub as mod


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

    pubsub._subscribers['myevent'] = [first, second]
    pubsub.publish('myevent', 1, 2, a='test')

    first.assert_called_once_with(1, 2, a='test')
    second.assert_called_once_with(1, 2, a='test')
    order_checker.assert_has_calls([mock.call('first'), mock.call('second')])


def test_subscribe_new(pubsub):
    assert 'test' not in pubsub._subscribers
    first = mock.Mock()
    second = mock.Mock()
    pubsub.subscribe('test', first)
    pubsub.subscribe('test', second)
    assert pubsub._subscribers['test'] == [first, second]


def test_subscribe_already_exists(pubsub):
    assert 'test' not in pubsub._subscribers
    func = mock.Mock()
    pubsub.subscribe('test', func)
    pubsub.subscribe('test', func)
    assert pubsub._subscribers['test'] == [func]


def test_unsubscribe(pubsub):
    func = mock.Mock()
    pubsub._subscribers['test'] = [func]
    pubsub.unsubscribe('test', func)
    assert pubsub._subscribers['test'] == []


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
