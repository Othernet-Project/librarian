import types

import mock
import pytest

import librarian.core.utils as mod


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
        dict(arg=2, batch_size=2, lazy=False),
        [0, 1, range(10), 3],
        dict(a=1, b=2),
        None,
        None,
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
    if ret_type is None:
        assert ret is ret_type
    else:
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