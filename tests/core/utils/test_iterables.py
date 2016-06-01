import types

import mock
import pytest

import librarian.core.utils.iterables as mod


# is_integral tests


@pytest.mark.parametrize('data,expected', [
    (1, True),
    (2.5, False),
    ("test", False),
    ([], False),
    ((), False),
    ((i for i in range(2)), False),
    ({}, False),
])
def test_is_integral(data, expected):
    assert mod.is_integral(data) is expected


# is_string tests


@pytest.mark.parametrize('data,expected', [
    (1, False),
    (2.5, False),
    ("test", True),
    (u"test2", True),
    ([], False),
    ((), False),
    ((i for i in range(2)), False),
    ({}, False),
])
def test_is_string(data, expected):
    assert mod.is_string(data) is expected


# is_iterable tests


@pytest.mark.parametrize('data,expected', [
    (1, False),
    (2.5, False),
    ("test", False),
    (u"test2", False),
    ([], True),
    ((), True),
    ((i for i in range(2)), True),
    ({}, False),
])
def test_is_iterable(data, expected):
    assert mod.is_iterable(data) is expected


# as_iterable tests


@pytest.mark.parametrize('params,in_args,in_kwargs,out_args,out_kwargs', [
    (None, [1, 2, 3], dict(a=3, b=4), [1, [2], 3], dict(a=3, b=4)),
    ([2, 'b'], [1, 2, 3], dict(a=3, b=4), [1, 2, [3]], dict(a=3, b=[4])),
    ([2, 'b'], [1, 2, [3]], dict(a=3, b=[4]), [1, 2, [3]], dict(a=3, b=[4])),
])
def test_as_iterable(params, in_args, in_kwargs, out_args, out_kwargs):
    fn = mock.Mock(__name__='myfn')
    decorated = mod.as_iterable(params=params)(fn)
    decorated(*in_args, **in_kwargs)
    fn.assert_called_once_with(*out_args, **out_kwargs)
