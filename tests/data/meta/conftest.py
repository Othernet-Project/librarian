import functools
import itertools
import os
import random
import string

import mock
import pytest

from squery_pg.pytest_fixtures import *


def random_sentence():
    nouns = ("marvin", "godzilla", "kirk", "picard", "everything")
    verbs = ("shoots", "jumps", "orders", "destroys", "is")
    adv = ("seemlessly", "dutifully", "foolishly", "bravely", "occasionally")
    adj = ("smart", "clueless", "weird", "secure", "awesome")
    idx = random.randrange(0, 5)
    return u' '.join([nouns[idx], verbs[idx], adv[idx], adj[idx]])


ALPHANUMERIC = filter(str.isalnum, string.printable)
KEY_VALUE_PAIRS = itertools.cycle([
    (u'width', 10),
    (u'height', 20),
    (u'duration', 120.35),
    (u'title', random_sentence),
    (u'description', random_sentence),
    (u'album', u'Some album'),
    (u'genre', u'Some genre'),
])
LANGUAGES = itertools.cycle([u'', u'en', u'de', u'ru', u'rs', u'es', u'pt',
                             u'ch', u'fr', u'it', u'gr', u'uk'])


def random_path_component():
    return u''.join(random.choice(ALPHANUMERIC) for i in range(10))


def random_path():
    return os.sep.join(random_path_component()
                       for i in range(random.randrange(1, 5)))


def random_subpath(base):
    return os.path.join(base, random_path_component())


def random_content_types(type_count=6):
    random_types = [random.randint(0, type_count - 1)
                    for _ in range(random.randint(1, type_count))]
    return functools.reduce(lambda acc, x: acc | 2 ** x, random_types, 0)


@pytest.fixture(scope='session')
def database_config():
    """
    Database configuration
    """
    return {
        'databases': [
            {'name': 'meta',
             'migrations': 'librarian.migrations.meta'}
        ],
        'conf': {},
    }


@pytest.fixture
def random_fs_datapoint(pk, parent_id, fs_type):
    row = {
        u'id': pk,
        u'parent_id': parent_id,
        u'path': random_path(),
        u'content_types': random_content_types(),
        u'type': fs_type,
    }
    return row


@pytest.fixture
def random_meta_datapoint(fs_data):
    (key, value) = next(KEY_VALUE_PAIRS)
    row = {
        u'fs_id': fs_data['id'],
        u'language': next(LANGUAGES),
        u'key': key,
        u'value': value() if callable(value) else value,
    }
    return row


@pytest.fixture
def random_dataset():
    """
    Factory for random fs and meta datasets. Returns a tuple of lists
    (fs_items, meta_items).
    """
    def _random_dataset(count=10):
        fs_data = [random_fs_datapoint(i, parent_id=0, fs_type=1)
                   for i in range(count / 2)]
        fs_data.extend(random_fs_datapoint(i, parent_id=1, fs_type=0)
                       for i in range(count / 2, count))
        # generate len(fs_data) ^ 2 meta entries, with the parent id
        # being randomly picked from the above generated fs entries
        fs_cycle = itertools.cycle(fs_data)
        metadata = [random_meta_datapoint(next(fs_cycle))
                    for i in range(count ** 2)]
        return (fs_data, metadata)
    return _random_dataset


@pytest.fixture
def populated_database(random_dataset, databases):
    (fs_data, metadata) = list(random_dataset())
    databases.load_fixtures('meta', 'fs', fs_data)
    databases.load_fixtures('meta', 'meta', metadata)
    return (fs_data, metadata, databases)


@pytest.fixture
def processors():
    proc1 = mock.Mock()
    proc1.name = 'generic'
    proc2 = mock.Mock()
    proc2.name = 'html'
    return (proc1, proc2)
