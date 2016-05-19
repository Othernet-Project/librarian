import functools
import os
import random
import string

import mock
import pytest

from squery_pg.pytest_fixtures import *


alphanumeric = filter(str.isalnum, string.printable)


def random_path_component():
    return ''.join(random.choice(alphanumeric) for i in range(10))


def random_path():
    return os.sep.join(random_path_component()
                       for i in range(random.randrange(1, 5)))


def random_subpath(base):
    return os.path.join(base, random_path_component())


def random_facet_types(type_count=5):
    random_types = [random.randint(0, type_count - 1)
                    for _ in range(random.randint(1, type_count))]
    return functools.reduce(lambda acc, x: acc | 2 ** x, random_types, 0)


def random_sentence():
    nouns = ("marvin", "godzilla", "kirk", "picard", "everything")
    verbs = ("shoots", "jumps", "orders", "destroys", "is")
    adv = ("seemlessly", "dutifully", "foolishly", "bravely", "occasionally")
    adj = ("smart", "clueless", "weird", "secure", "awesome")
    idx = random.randrange(0, 5)
    return ' '.join([nouns[idx], verbs[idx], adv[idx], adj[idx]])


@pytest.fixture(scope='session')
def database_config():
    """
    Database configuration
    """
    return {
        'databases': [
            {'name': 'facets',
             'migrations': 'librarian.migrations.facets'}
        ],
        'conf': {},
    }


@pytest.fixture
def random_folder_datapoint(pk):
    row = {
        'id': pk,
        'path': random_path(),
        'facet_types': random_facet_types(),
        'main': None,
    }
    return row


@pytest.fixture
def random_facet_datapoint(folder):
    row = {
        'path': random_subpath(folder['path']),
        'facet_types': random_facet_types(),
        'folder': folder['id'],
        'title': random_sentence(),
    }
    return row


@pytest.fixture
def random_dataset():
    """
    Factory for random facet and folder datasets. Returns a tuple of lists
    (folders, facets).
    """
    def _random_dataset(count=5):
        folder_data = [random_folder_datapoint(i) for i in range(count)]
        # generate len(folder_data) ^ 2 facet entries, with the parent folder
        # being randomly picked from the above generated folder entries
        facet_data = [random_facet_datapoint(random.choice(folder_data))
                      for i in range(count ** 2)]
        return (folder_data, facet_data)
    return _random_dataset


@pytest.fixture
def populated_database(random_dataset, databases):
    (folder_data, facet_data) = list(random_dataset())
    databases.load_fixtures('facets', 'folders', folder_data)
    databases.load_fixtures('facets', 'facets', facet_data)
    return folder_data, facet_data, databases


@pytest.fixture
def processors():
    proc1 = mock.Mock()
    proc1.name = 'generic'
    proc2 = mock.Mock()
    proc2.name = 'html'
    return (proc1, proc2)
