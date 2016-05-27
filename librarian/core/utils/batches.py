"""
Functions and decorators for breaking up large collections into batches.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
import functools
import itertools


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


class aggregator(object):
    """
    Base py:class:`aggregator`, meant only to provide the skeleton for
    subclasses.
    """
    type = None
    method = None


class appender(aggregator):
    """
    Appends each result set to a list.
    """
    type = list
    method = staticmethod(lambda agg, x: agg.append(x))


class extender(aggregator):
    """
    Extends the aggregator list with each result set.
    """
    type = list
    method = staticmethod(lambda agg, x: agg.extend(x))


class updater(aggregator):
    """
    Updates the aggregator dict with each result set.
    """
    type = dict
    method = staticmethod(lambda agg, x: agg.update(x))


class batched(object):
    """
    Decorator that makes the specified iterable by index (``arg``) or by name
    (``kwarg``) of a function call split up into batches, and calls the wrapped
    function with batches of that data.
    If ``aggregator`` is specified, the results will be collected into a new
    instance of py:attr:`aggregator.type`, using py:attr:`aggregator.method`
    (defined on the same py:class:`aggregator` class) and returned, otherwise
    it yields the result(s) of the calls individually.
    ``lazy`` is used in case no ``aggregator`` was specified, and it determines
    whether a generator will be returned, or the batches will be evaluated
    in-place.
    """
    #: Generic aggregators
    appender = appender
    extender = extender
    updater = updater

    def __init__(self, arg=None, kwarg=None, batch_size=1000, aggregator=None,
                 lazy=True):
        # proper interface usage checks
        if not arg and not kwarg:
            raise TypeError("Either ``arg`` or ``kwarg`` is needed.")
        if arg and kwarg:
            raise TypeError("Cannot use both ``arg`` and ``kwarg``.")
        self._index = arg
        self._name = kwarg
        self._batch_size = batch_size
        self._aggregator = aggregator
        self._lazy = lazy

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
            if self._aggregator:
                result = self._aggregator.type()
                aggregator = functools.partial(self._aggregator.method, result)
            # perform batched invocation of ``fn``
            generator = self._invoke(fn, args, kwargs, batchable, aggregator)
            # if no aggregation was requested, return the generator itself
            if not self._aggregator and self._lazy:
                return generator
            # otherwise evaluate generator and return the collected results
            list(generator)
            return result
        return wrapper
