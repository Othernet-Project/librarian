from collections import deque

from .contrib.databases.utils import *  # NOQA


class muter(object):
    """
    Iterator that can be mutated while being iterated over.

    Example::

        >>> more_items = iter([4, 5, 6])
        >>> def appender(obj):
        ...    for i in more_items:
        ...        obj.append(i)
        ...
        >>> m = muter([1, 2, 3])
        >>> out = []
        >>> for i in m:
        ...    appender(m)
        ...    out.append(i)
        >>> out
        [1, 2, 3, 4, 5, 6]
        >>> list(m)
        []
        >>> m.reset()
        >>> list(m)
        [1, 2, 3, 4, 5, 6]

    """
    def __init__(self, iter=[]):
        self._iter = deque(iter)
        self._past = deque()

    def reset(self):
        """
        Reset the iterator to original state.
        """
        self._past.extend(self._iter)
        self._iter = self._past
        self._past = deque()

    def append(self, element):
        """
        Append a new element to the end of the iterator. This method can be
        called even during iteration, and will not cause the iteration to end
        in an exception.
        """
        self._iter.append(element)

    def next(self):
        try:
            current = self._iter.popleft()
        except IndexError:
            raise StopIteration()
        self._past.append(current)
        return current

    def __iter__(self):
        while True:
            yield self.next()
