from collections import deque

from .contrib.databases.utils import *  # NOQA


class muter(object):
    """
    Iterator that can be mutated while being iterated over.

    The :py:class:`muter` objects support ``len()``, but not ``reversed(d)``.
    Membership test with ``in`` operator is also supported.

    The ``len()`` call to a :py:class:`muter` object is stable during iteration
    (always returns the *current* length of the iterator, including items that
    have already been iterated over). The number of remaining elements can be
    obtained by accessing the :py:attr:`~muter.remaining` attribute.

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
        >>> list(m)
        []
        >>> len(m)
        6
        >>> m.reset()
        >>> for i in m:
        ...    print(m.remaining)
        ...
        5
        4
        3
        2
        1

    """
    def __init__(self, iter=[]):
        self._iter = deque(iter)  # items to iterate over
        self._past = deque()      # items that have been iterated over

    def __len__(self):
        return len(self._iter) + len(self._past)

    def reset(self):
        """
        Reset the iterator to original state.
        """
        self._past.extend(self._iter)
        self._iter = self._past
        self._past = deque()

    @property
    def remaining(self):
        """
        Returns the number of items left in iteration.
        """
        return len(self._iter)

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
