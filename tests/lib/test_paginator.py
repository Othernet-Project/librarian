import mock
import pytest

from librarian.lib import paginator as mod


@pytest.fixture
def paginator():
    return mod.Paginator(range(10), 1, 20)


def test__in_range(paginator):
    assert paginator._in_range(0, 1, 10) == 1
    assert paginator._in_range(11, 1, 10) == 10
    assert paginator._in_range(5, 1, 10) == 5


def test__choice_range(paginator):
    assert paginator._choice_range(1, 3) == [(1, 1), (2, 2)]
    assert paginator._choice_range(1, 6, 2) == [(1, 1), (3, 3), (5, 5)]


@mock.patch.object(mod.Paginator, '_choice_range')
def test_page_choices(_choice_range, paginator):
    paginator.page_choices
    _choice_range.assert_called_once_with(1, 2)


@mock.patch.object(mod.Paginator, '_choice_range')
def test_per_page_choices(_choice_range, paginator):
    paginator.per_page_choices
    _choice_range.assert_called_once_with(20, 100, 10)


def test_pages(paginator):
    assert mod.Paginator(range(100), 1, 20).pages == 5
    assert mod.Paginator(range(1000), 1, 30).pages == 34


def test_has_next():
    assert mod.Paginator(range(100), 1, 20).has_next
    assert not mod.Paginator(range(10), 1, 20).has_next
    assert not mod.Paginator(range(100), 5, 20).has_next


def test_has_prev():
    assert mod.Paginator(range(100), 3, 20).has_prev
    assert not mod.Paginator(range(10), 1, 20).has_prev
    assert not mod.Paginator(range(100), 1, 20).has_prev


def test_items():
    assert mod.Paginator(range(100), 3, 20).items == range(40, 60)
    assert mod.Paginator(range(100), 1, 30).items == range(0, 30)
    assert mod.Paginator(range(110), 4, 30).items == range(90, 110)


def test_parse_int():
    assert mod.Paginator._parse_int({'test': 2}, 'test', 10) == 2
    assert mod.Paginator._parse_int({'test': 2}, 'invalid', 10) == 10
    assert mod.Paginator._parse_int({'test': 'garbage'}, 'test', 10) == 10
    assert mod.Paginator._parse_int({'test': None}, 'test', 10) == 10


@mock.patch.object(mod.Paginator, '_parse_int')
def test_parse_per_page(_parse_int, paginator):
    params = {'a': 1}

    paginator.parse_per_page(params)
    paginator.parse_per_page(params, param_name='perpage', default=30)
    _parse_int.assert_has_calls([mock.call(params, 'pp', 20),
                                 mock.call(params, 'perpage', 30)])


@mock.patch.object(mod.Paginator, '_parse_int')
def test_parse_page(_parse_int, paginator):
    params = {'a': 1}

    paginator.parse_page(params)
    paginator.parse_page(params, param_name='page', default=4)
    _parse_int.assert_has_calls([mock.call(params, 'p', 1),
                                 mock.call(params, 'page', 4)])
