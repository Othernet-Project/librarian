import functools
import itertools
import numbers

from .contrib.databases.utils import *  # NOQA


def is_integral(obj):
    """
    Determine whether the passed in object is a number of integral type.
    """
    return isinstance(obj, numbers.Integral)


def is_string(obj):
    """
    Determine if the passed in object is a string.
    """
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def is_iterable(obj):
    """
    Determine if the passed in object is an iterable, but not a string or dict.
    """
    return (hasattr(obj, '__iter__') and
            not isinstance(obj, dict) and
            not is_string(obj))


def as_iterable(params=None):
    """
    Make sure the marked parameters are iterable. In case a single-unwrapped
    parameter is found among them (e.g. an int, string, ...), wrap it in a
    list and forward like that to the wrapped function. The marked parameters,
    if not explicitly specified, defaults to the 1st argument (``args[1]``).
    """
    # set up default converter and separate positional from keyword arguments
    params = params or [1]
    indexes = [i for i in params if is_integral(i)]
    keys = [k for k in params if is_string(k)]

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # patch positional arguments, if needed
            if indexes:
                # copy args into a list as it's a tuple by default
                args = list(args)
                for idx in indexes:
                    if not is_iterable(args[idx]):
                        args[idx] = [args[idx]]
            # patch keyword arguments, if needed
            if keys:
                for key in keys:
                    if not is_iterable(kwargs[key]):
                        kwargs[key] = [kwargs[key]]
            # invoke ``fn`` with patched parameters
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def batches(data, batch_size=1000):
    """
    Batches of ``batch_size`` items ceated from ``data`` iterable.
    """
    data = iter(data)
    while True:
        batch = list(itertools.islice(data, batch_size))
        if not batch:
            break
        yield batch


class batched(object):
    """
    Decorator that makes the specified iterable by index (``arg``) or by name
    (``kwarg``) of a function call split up into batches, and calls the wrapped
    function with batches of that data.
    If ``aggregate`` is set, the results will be collected into a list and
    returned, otherwise it yields the result(s) of the calls individually.
    The parameter ``flat`` is used only if ``aggregate`` is set, and it implies
    that the wrapped function returns a list or tuple. When set, during
    aggregation the aggregator list will be extended with the result set,
    instead of appending to it.
    """
    def __init__(self, arg=None, kwarg=None, batch_size=1000, aggregate=False,
                 flat=False):
        # proper interface usage checks
        if not arg and not kwarg:
            raise TypeError("Either ``arg`` or ``kwarg`` is needed.")
        if arg and kwarg:
            raise TypeError("Cannot use both ``arg`` and ``kwarg``.")
        self._index = arg
        self._name = kwarg
        self._batch_size = batch_size
        self._aggregate = aggregate
        self._flat = flat

    def _invoke(self, fn, args, kwargs, batchable, aggregator):
        for batch in batches(batchable, self._batch_size):
            # inject the batched param back into the passed in arguments
            # or keyword arguments for the callable function
            if self._index:
                args[self._index] = batch
            else:
                kwargs[self._name] = batch
            # invoke function with patched parameters
            result = fn(*args, **kwargs)
            if aggregator:
                aggregator(result)
            else:
                yield result

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # get the value that needs to be batched
            if self._index:
                batchable = args[self._index]
                # args must support item assignment
                args = list(args)
            else:
                batchable = kwargs[self._name]
            # set up result aggregator if it's needed
            result = aggregator = None
            if self._aggregate:
                result = []
                aggregator = result.extend if self._flat else result.append
            # perform batched invocation of ``fn``
            generator = self._invoke(fn, args, kwargs, batchable, aggregator)
            # if no aggregation was requested, return the generator itself
            if not self._aggregate:
                return generator
            # otherwise evaluate generator and return the collected results
            list(generator)
            return result
        return wrapper
