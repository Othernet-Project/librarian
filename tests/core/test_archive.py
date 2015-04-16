import mock
import pytest

import librarian.core.archive as mod


MOD = mod.__name__


@pytest.fixture
def mocked_backend():
    backend = mock.MagicMock(spec=mod.BaseArchive)
    init_flag = '_{0}__initialized'.format(mod.BaseArchive.__name__)
    setattr(backend, init_flag, True)
    return backend


class TestArchive(object):

    def test_init_invalid_backend(self):
        with pytest.raises(TypeError):
            mod.Archive(mock.MagicMock())

    def test_init_uninitialized_backend(self):
        with pytest.raises(RuntimeError):
            mod.Archive(mock.MagicMock(spec=mod.BaseArchive))

    def test_init_success(self, mocked_backend):
        archive = mod.Archive(mocked_backend)
        assert object.__getattribute__(archive, 'backend') is mocked_backend

    def test_archive_attr_access(self, mocked_backend):
        some_func = mock.Mock()
        mocked_backend.some_func = some_func
        archive = mod.Archive(mocked_backend)
        archive.some_func('param')
        some_func.assert_called_once_with('param')

    def test_archive_attr_set(self, mocked_backend):
        archive = mod.Archive(mocked_backend)

        with pytest.raises(AttributeError):
            object.__getattribute__(archive, 'test_attr')
        with pytest.raises(AttributeError):
            object.__getattribute__(mocked_backend, 'test_attr')

        archive.test_attr = 1

        with pytest.raises(AttributeError):
            object.__getattribute__(archive, 'test_attr')

        object.__getattribute__(mocked_backend, 'test_attr')

    @mock.patch('__builtin__.__import__')
    def test_get_backend_class_on_pythonpath(self, import_func):
        import_func.side_effect = mock.Mock()
        mod.Archive.get_backend_class('path.to.package.module.ClassName')
        import_func.assert_called_once_with('path.to.package.module.ClassName',
                                            fromlist=['ClassName'])

    def test_get_backend_class_not_on_pythonpath(self):
        original_import = __import__

        def mocked_import(package, *args, **kwargs):
            if package == 'localpkg.mod.ClassName':
                raise ImportError()

            if 'fromlist' not in kwargs:
                return original_import(package, *args, **kwargs)

            assert package == 'librarian.core.backends.localpkg.mod'
            assert kwargs['fromlist'] == ['ClassName']
            return mock.Mock(ClassName='backend_cls')

        with mock.patch('__builtin__.__import__') as import_func:
            import_func.side_effect = mocked_import
            cls = mod.Archive.get_backend_class('localpkg.mod.ClassName')
            assert cls == 'backend_cls'

    @mock.patch.object(mod.Archive, '__init__')
    @mock.patch.object(mod.Archive, 'get_backend_class')
    def test_setup(self, get_backend_class, init_func):
        mocked_backend = mock.Mock()
        mocked_backend_cls = mock.Mock()
        mocked_backend_cls.return_value = mocked_backend
        get_backend_class.return_value = mocked_backend_cls
        init_func.return_value = None

        mod.Archive.setup('backend_path', 1, 2, kw3=3, kw4=4)

        get_backend_class.assert_called_once_with('backend_path')
        mocked_backend_cls.assert_called_once_with(1, 2, kw3=3, kw4=4)
        init_func.assert_called_once_with(mocked_backend)


@pytest.fixture
def base_archive():
    return mod.BaseArchive(content_dir='unimportant')


class TestBaseArchive(object):

    def test_base_archive_init_fail(self):
        with pytest.raises(TypeError):
            mod.BaseArchive()

    def test_base_archive_init_success(self):
        archive = mod.BaseArchive(content_dir='test')
        init_flag = '_{0}__initialized'.format(mod.BaseArchive.__name__)
        assert hasattr(archive, init_flag)

    @mock.patch(MOD + '.os')
    @mock.patch(MOD + '.get_zip_path')
    @mock.patch.object(mod.BaseArchive, 'remove_meta_from_db')
    def test_remove_silent_failure(self, remove_meta_from_db, get_zip_path, os,
                                   base_archive):
        # FIXME: This needs to be an integration test for full cov
        hashes = ['foo', 'bar', 'baz']
        get_zip_path.return_value = 'foo'
        os.unlink.side_effect = [OSError, None, None]  # first file fails
        ret = base_archive.remove_from_archive(hashes)
        # Deletes three items even though first one fails
        remove_meta_from_db.assert_called_once_with(hashes)
        assert ret == ['foo']

    @mock.patch(MOD + '.os')
    @mock.patch(MOD + '.get_zip_path')
    @mock.patch.object(mod.BaseArchive, 'remove_meta_from_db')
    def test_remove_failure_when_path_is_none(self, remove_meta_from_db,
                                              get_zip_path, os, base_archive):
        # FIXME: This needs to be an integration test for full cov
        get_zip_path.return_value = None
        hashes = ['foo', 'bar', 'baz']
        try:
            ret = base_archive.remove_from_archive(hashes)
        except Exception:
            assert False, 'Expected not to raise'

        remove_meta_from_db.assert_called_once_with(hashes)
        assert ret == hashes
