import types

import mock
import pytest

import librarian.core.utils as mod


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


# batches tests

@pytest.mark.parametrize('size,out', [
    (2, [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]),
    (3, [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]),
    (5, [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
    (10, [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
    (20, [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
    (0, []),
])
def test_batch(size, out):
    source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert list(mod.batches(source, size)) == out


# batched tests


@pytest.mark.parametrize('opts,in_args,in_kwargs,ret_type,ret_data,batches', [
    (
        dict(kwarg='b', batch_size=2),
        [0, 1, 2, 3],
        dict(a=1, b=range(10)),
        types.GeneratorType,
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
    ), (
        dict(arg=2, batch_size=2),
        [0, 1, range(10), 3],
        dict(a=1, b=2),
        types.GeneratorType,
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
    ), (
        dict(arg=2, batch_size=2, aggregator=mod.batched.appender),
        [0, 1, range(10), 3],
        dict(a=1, b=2),
        list,
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
    ), (
        dict(arg=2, batch_size=2, aggregator=mod.batched.extender),
        [0, 1, range(10), 3],
        dict(a=1, b=2),
        list,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
    ), (
        dict(arg=2, batch_size=2, aggregator=mod.batched.updater),
        [0, 1, [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)], 3],
        dict(a=1, b=2),
        dict,
        {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
        [[(0, 0), (1, 1)], [(2, 2), (3, 3)], [(4, 4)]],
    )
])
def test_batched(opts, in_args, in_kwargs, ret_type, ret_data, batches):
    mocked_fn = mock.Mock(__name__='myfn')

    def wrapped(*args, **kwargs):
        if 'arg' in opts:
            return args[opts['arg']]
        return kwargs[opts['kwarg']]
    # noop fn that returns the passed in batch
    mocked_fn.side_effect = wrapped
    fn = mod.batched(**opts)(mocked_fn)
    ret = fn(*in_args, **in_kwargs)
    # check return type
    assert isinstance(ret, ret_type)
    # check returned data from batches
    if isinstance(ret, types.GeneratorType):
        for (result, expected) in zip(ret, ret_data):
            assert result == expected
    else:
        assert ret == ret_data
    # check if wrapped fn was called with correct args
    calls = []
    for batch in batches:
        args = list(in_args)
        kwargs = dict(in_kwargs)
        if 'arg' in opts:
            args[opts['arg']] = batch
        else:
            kwargs[opts['kwarg']] = batch
        calls.append(mock.call(*args, **kwargs))
    mocked_fn.assert_has_calls(calls)
