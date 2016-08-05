import mock
import pytest

from librarian.data.state import container as mod


@pytest.fixture
def container():
    return mod.StateContainer(cache=mock.Mock(),
                              events=mock.Mock())


def test___get_key(container):
    exp = 'state-{}-testprov'.format(container._id)
    assert container._StateContainer__get_key('testprov') == exp


def test___get(container):
    container._StateContainer__get('testkey')
    container._cache.get.assert_called_once_with('testkey')


def test___set(container):
    testprov = mock.Mock()
    container._registry['testprov'] = testprov
    assert not container._changed
    container._StateContainer__set('testprov', 'testkey', 42, timeout=5)

    container._cache.set.assert_called_once_with('testkey', 42, timeout=5)
    container._events.publish.assert_called_once_with(
        container.STATE_CHANGED_EVENT,
        provider=testprov
    )
    assert list(container._changed) == ['testprov']


def test___onchange(container):
    cb = mock.Mock()
    container._StateContainer__onchange('testprov', cb)
    assert container._events.subscribe.called
    (args, kwargs) = container._events.subscribe.call_args
    assert args == (container.STATE_CHANGED_EVENT, cb)
    assert callable(kwargs['condition'])


def test_provider_access(container):
    prov = mock.Mock()
    container._registry['prov'] = prov
    assert container.provider('prov') is prov


def test_provider_value_access(container):
    prov = mock.Mock()
    container._registry['prov'] = prov
    assert container['prov'] == prov.get.return_value
    assert container.prov == prov.get.return_value


def test_register_already_exists(container):
    container._registry['prov'] = mock.Mock()
    twin = mock.Mock()
    twin.name = 'prov'
    with pytest.raises(ValueError):
        container.register(twin)


def test_register_success(container):
    prov = mock.Mock()
    prov.name = 'test_provider'
    container.register(prov)
    assert container._registry['test_provider'] is prov.return_value
    assert all([key in prov.call_args[1]
                for key in ('getter', 'setter', 'onchange')])


def test_fetch_changes(container):
    prov1 = mock.Mock()
    prov2 = mock.Mock()
    prov3 = mock.Mock()
    container._registry.update(prov1=prov1, prov2=prov2, prov3=prov3)
    container._changed.add('prov1')
    container._changed.add('prov3')
    assert container.fetch_changes() == {'prov1': prov1, 'prov3': prov3}
    assert not container._changed
