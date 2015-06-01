"""
pagnation.py: Pagination class

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import math


class Paginator(object):
    min_per_page = 20
    max_per_page = 100

    def __init__(self, items, page, per_page):
        self._items = items
        self.per_page = self._in_range(per_page,
                                       self.min_per_page,
                                       self.max_per_page)
        self.page = self._in_range(page, 1, self.pages)

    def _in_range(self, value, start, end):
        return min(end, max(start, value))

    def _choice_range(self, start, end, skip=1):
        choices = range(start, end, skip)
        return zip(choices, choices)

    @property
    def page_choices(self):
        return self._choice_range(1, self.pages + 1)

    @property
    def per_page_choices(self):
        return self._choice_range(self.min_per_page, self.max_per_page, 10)

    @property
    def pages(self):
        return int(math.ceil(len(self._items) / float(self.per_page)))

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def items(self):
        first = (self.page - 1) * self.per_page
        last = first + self.per_page
        return self._items[first:last]

    @classmethod
    def _parse_int(cls, params, param_name, default):
        try:
            return int(params.get(param_name))
        except (ValueError, TypeError):
            return default

    @classmethod
    def parse_per_page(cls, params, param_name='pp', default=20):
        return cls._parse_int(params, param_name, default)

    @classmethod
    def parse_page(cls, params, param_name='p', default=1):
        return cls._parse_int(params, param_name, default)
