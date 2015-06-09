import mock
import pytest

from librarian.utils import exts as mod


def test_placeholder():
    placeholder = mod.Placeholder()
    assert isinstance(placeholder(1, 2, a='b'), mod.Placeholder)
    assert isinstance(placeholder.test_func(1, 2, a='b'), mod.Placeholder)


def test_add_extension():
    exts = mod.ExtContainer()
    assert exts._extensions == {}
    exts.first = 1
    exts['second'] = 2
    assert exts._extensions == {'first': 1, 'second': 2}


def test_access_extension():
    test_ext = mock.Mock()
    exts = mod.ExtContainer()
    exts.important = test_ext
    exts.important(1, 2)
    test_ext.assert_called_once_with(1, 2)
    try:
        exts.not_installeld('cache')
    except Exception:
        pytest.fail("Should not care whether it exists or not.")


def test_is_installed():
    exts = mod.ExtContainer()
    exts['valid'] = 1
    assert exts.is_installed('valid')
    assert not exts.is_installed('missing')
