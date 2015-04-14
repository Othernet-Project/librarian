import mock

from librarian.core import backend, Delegator


def test_delegator_assignment():
    assert 'test' not in dir(backend)
    backend.test
    assert 'test' in dir(backend)
    assert isinstance(backend.test, Delegator)


@mock.patch('__builtin__.__import__')
def test__get_backend_package_pythonpath(import_func):
    import_func.side_effect = mock.Mock()
    backend._get_backend_package('path.to.package')
    import_func.assert_called_once_with('path.to.package',
                                        fromlist=['package'])


def test__get_backend_package_local():
    original_import = __import__

    def mocked_import(package, *args, **kwargs):
        if package == 'localpackage':
            raise ImportError()

        if 'fromlist' not in kwargs:
            return original_import(package, *args, **kwargs)

        assert package == 'librarian.core.backends.localpackage'
        assert kwargs['fromlist'] == ['localpackage']

    with mock.patch('__builtin__.__import__') as import_func:
        import_func.side_effect = mocked_import
        backend._get_backend_package('localpackage')


@mock.patch('__builtin__.__import__')
@mock.patch('pkgutil.iter_modules')
def test__install_modules(iter_modules, import_func):
    backend.mod1  # make one of the delegators already installed

    assert 'mod1' in dir(backend)
    assert 'mod2' not in dir(backend)
    assert 'mod3' not in dir(backend)

    iter_modules.return_value = (
        (None, 'mod1', False),
        (None, 'mod2', False),
        (None, 'mod3', False),
    )
    mocked_pkg = mock.MagicMock(__path__='path.to.package',
                                __name__='package')
    backend._install_modules(mocked_pkg)

    iter_modules.assert_called_once_with(mocked_pkg.__path__)
    calls = [
        mock.call('package.mod1', fromlist=['mod1']),
        mock.call('package.mod2', fromlist=['mod2']),
        mock.call('package.mod3', fromlist=['mod3'])
    ]
    import_func.assert_has_calls(calls)

    assert 'mod1' in dir(backend)
    assert 'mod2' in dir(backend)
    assert 'mod3' in dir(backend)


@mock.patch.object(backend, '_install_modules')
@mock.patch.object(backend, '_get_backend_package')
def test_setup(get_backend_package, install_modules):
    assert not backend._loaded
    mocked_pkg = mock.Mock()
    get_backend_package.return_value = mocked_pkg

    backend.setup('mybackend', {'param': 1}, 'storage')

    get_backend_package.assert_called_once_with('mybackend')
    install_modules.assert_called_once_with(mocked_pkg)
    assert backend._loaded
