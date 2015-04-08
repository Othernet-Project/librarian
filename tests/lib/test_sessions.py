import datetime
import json

import mock
import pytest

from librarian.lib import sessions as mod

from .base import transaction_test


MOD = mod.__name__


def get_session(session_id):
    db = mod.request.db.sessions
    query = db.Select(sets='sessions', where='session_id = ?')
    db.query(query, session_id)
    return db.result


def add_session(session_data):
    db = mod.request.db.sessions
    query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
    db.execute(query, session_data)


def assert_session_count_is(expected):
    db = mod.request.db.sessions
    query = db.Select('COUNT(*) as count', sets='sessions')
    db.query(query)
    session_count = db.result.count
    assert session_count == expected


@transaction_test(MOD + '.request')
def test_session_plugin_create():
    mod.request.get_cookie.return_value = None
    mod.request.app.config = {'session.lifetime': 1}

    cookie_name = 'session_cookie'
    secret = 'mischief managed'

    callback = mock.Mock(__name__='callback')
    plugin = mod.session_plugin(cookie_name=cookie_name, secret=secret)
    wrapped = plugin(callback)
    wrapped('test')

    assert_session_count_is(1)

    sess = get_session(mod.request.session.id)
    assert sess['data'] == '{}'
    assert sess['session_id'] == mod.request.session.id
    assert isinstance(sess['expires'], datetime.datetime)

    callback.assert_called_once_with('test')


@transaction_test(MOD + '.request')
def test_use_existing_session():
    cookie_name = 'session_cookie'
    secret = 'mischief managed'

    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    add_session({'session_id': session_id,
                 'data': json.dumps(data),
                 'expires': expires})

    mod.request.get_cookie.return_value = session_id

    callback = mock.Mock(__name__='callback')
    plugin = mod.session_plugin(cookie_name=cookie_name, secret=secret)
    wrapped = plugin(callback)
    wrapped('test')

    assert_session_count_is(1)

    assert mod.request.session.data == data
    assert mod.request.session.id == session_id
    assert mod.request.session.expires == expires

    callback.assert_called_once_with('test')


@transaction_test(MOD + '.request')
def test_session_invalid():
    with pytest.raises(mod.SessionInvalid):
        mod.Session.fetch(None)

    with pytest.raises(mod.SessionInvalid):
        mod.Session.fetch('not valid')


@transaction_test(MOD + '.request')
def test_session_expired():
    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
    add_session({'session_id': session_id,
                 'data': json.dumps(data),
                 'expires': expires})

    assert_session_count_is(1)

    with pytest.raises(mod.SessionExpired):
        mod.Session.fetch(session_id)

    assert_session_count_is(0)


@transaction_test(MOD + '.request')
def test_save_session():
    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
    add_session({'session_id': session_id,
                 'data': json.dumps(data),
                 'expires': expires})

    assert_session_count_is(1)

    s = mod.Session.fetch(session_id)
    assert s.id == session_id
    assert s.data == data

    s['second'] = 'new'
    s.save()

    assert_session_count_is(1)

    s = mod.Session.fetch(session_id)
    assert s.id == session_id
    assert s.data == {'some': 'thing', 'second': 'new'}


@transaction_test(MOD + '.request')
def test_rotate_session():
    mod.request.app.config = {'session.lifetime': 1}
    s = mod.Session.create()
    s['test'] = 123
    s.save()

    assert_session_count_is(1)

    old_session_id = s.id
    old_data = s.data.copy()

    s.rotate()
    assert s.id != old_session_id
    assert s.data == old_data

    assert_session_count_is(1)


@transaction_test(MOD + '.request')
def test_modified():
    mod.request.app.config = {'session.lifetime': 1}
    s = mod.Session.create()
    assert not s.modified

    s.expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
    assert s.modified

    s.save()
    assert not s.modified

    s['a'] = 1
    assert s.modified

    s.save()
    assert not s.modified

    del s['a']
    assert s.modified

    s.save()
    assert not s.modified

    s.rotate()
    assert not s.modified

    with pytest.raises(mod.SessionExpired):
        s.expire()
    assert not s.modified

    s.delete()
    assert not s.modified
