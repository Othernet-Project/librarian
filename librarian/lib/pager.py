"""
pager.py: Common pager utilities

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import division

import math

from bottle import request, response


class Pager(object):
    MIN_PER_PAGE = 20
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 20
    MAX_COOKIE_AGE = 365 * 24 * 60 * 60

    def __init__(self, objects=[], page=1, per_page=DEFAULT_PER_PAGE, pid=''):
        self.objects = objects
        self.page = page
        self.per_page = per_page
        self.pages = 0
        self.recalculate_num_pages()
        self.pid = pid
        self.cookie_name = 'pager_%s' % self.pid if self.pid else 'pager'

    def recalculate_num_pages(self):
        self.pages = int(math.ceil(self.get_total_count() / self.per_page))

    def get_total_count(self):
        if type(self.objects) == int:
            return self.objects
        return len(self.objects)

    def remember_perpage(self):
        response.set_cookie(self.cookie_name, str(self.per_page),
                            max_age=self.MAX_COOKIE_AGE)

    def get_stored_perpage(self):
        return request.cookies.get(self.cookie_name)

    def get_paging_params(self):
        """
        Obtain paging params from the request context.
        """
        try:
            per_page = int(request.params.get('pp', self.get_stored_perpage()))
        except (ValueError, TypeError):
            per_page = self.DEFAULT_PER_PAGE
        # Cap the per_page value
        per_page = min([self.MAX_PER_PAGE, per_page])
        per_page = max([self.MIN_PER_PAGE, per_page])
        self.per_page = per_page
        self.remember_perpage()
        self.recalculate_num_pages()
        try:
            page = int(request.params.get('p', 1))
        except ValueError:
            page = 1
        # Cap the page value
        page = max([1, page])
        page = min([self.pages, page])
        self.page = page

    def get_item_ranges(self):
        """
        Return two-tuple of first and last index of the range.
        """
        first = (self.page - 1) * self.per_page
        last = first + self.per_page  # We ignore overshoot
        return first, last

    def get_items(self):
        """
        Get items that match the current page.
        """
        first, last = self.get_item_ranges()
        return self.objects[first:last]

    @property
    def pager_choices(self):
        return [(i, i) for i in range(1, self.pages + 1)]

    @property
    def per_page_choices(self):
        return [(i, i)
                for i in range(self.MIN_PER_PAGE, self.MAX_PER_PAGE, 10)]

    @property
    def offset(self):
        return (self.page - 1) * self.per_page
