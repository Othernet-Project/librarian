from collections import deque

from .contrib.databases.utils import *  # NOQA


class muter(object):
    """
    Iterator that can be mutated while being iterated over.
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
