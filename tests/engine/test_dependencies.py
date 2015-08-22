import pytest

from librarian.engine import dependencies as mod


def test__parse():
    dep_tree = mod.collections.OrderedDict()
    dep_tree['a'] = {'fn': 'afn', 'depends_on': ['b']}
    dep_tree['b'] = {'fn': 'bfn', 'depends_on': ['c']}
    dep_tree['c'] = {'fn': 'cfn', 'required_by': ['a']}
    dep_tree['d'] = {'fn': 'dfn',
                     'depends_on': ['c'],
                     'required_by': ['a', 'b']}

    loader = mod.DependencyLoader(['a', 'b', 'c'], {})
    loader._dep_tree = dep_tree
    loader._parse()

    expected = mod.collections.OrderedDict()
    expected['a'] = {'fn': 'afn', 'depends_on': ['b', 'c', 'd']}
    expected['b'] = {'fn': 'bfn', 'depends_on': ['c', 'd']}
    expected['c'] = {'fn': 'cfn'}
    expected['d'] = {'fn': 'dfn', 'depends_on': ['c']}
    assert loader._dep_tree == expected


def test__order_simple():
    dep_tree = mod.collections.OrderedDict()
    dep_tree['a'] = {'fn': 'afn'}
    dep_tree['b'] = {'fn': 'bfn', 'depends_on': ['d', 'c']}
    dep_tree['c'] = {'fn': 'cfn'}
    dep_tree['d'] = {'fn': 'dfn', 'depends_on': ['a']}

    loader = mod.DependencyLoader(['a', 'b', 'c'], {})
    loader._dep_tree = dep_tree
    loader._order()

    expected = mod.collections.OrderedDict()
    expected['a'] = {'fn': 'afn'}
    expected['c'] = {'fn': 'cfn'}
    expected['d'] = {'fn': 'dfn', 'depends_on': ['a']}
    expected['b'] = {'fn': 'bfn', 'depends_on': ['d', 'c']}
    assert loader._dep_tree == expected


def test__order_circular_dependency():
    dep_tree = mod.collections.OrderedDict()
    dep_tree['a'] = {'fn': 'afn'}
    dep_tree['b'] = {'fn': 'bfn', 'depends_on': ['d', 'c']}
    dep_tree['c'] = {'fn': 'cfn', 'depends_on': ['b']}
    dep_tree['d'] = {'fn': 'dfn', 'depends_on': ['b']}

    loader = mod.DependencyLoader(['a', 'b', 'c'], {})
    loader._dep_tree = dep_tree
    with pytest.raises(mod.CircularDependency):
        loader._order()


def test__order_missing_dependency():
    dep_tree = mod.collections.OrderedDict()
    dep_tree['a'] = {'fn': 'bfn', 'depends_on': ['b']}
    dep_tree['b'] = {'fn': 'cfn', 'depends_on': ['invalid']}

    loader = mod.DependencyLoader(['a', 'b'], {})
    loader._dep_tree = dep_tree
    with pytest.raises(mod.UnresolvableDependency):
        loader._order()
