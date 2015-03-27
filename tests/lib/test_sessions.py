import datetime
import json

import bottle
import mock
import pytest

from librarian.lib import sessions

from .base import transaction_test


@mock.patch('bottle.response.set_cookie')
@transaction_test
def test_create_new_session(set_cookie):
    bottle.request.get_cookie.return_value = None

    cookie_name = 'session_cookie'
    lifetime = 10
    secret = 'mischief managed'

    callback = mock.Mock(__name__='callback')
    plugin = sessions.session_plugin(cookie_name=cookie_name,
                                     lifetime=10,
                                     secret=secret)
    wrapped = plugin(callback)
    wrapped('test')

    db = bottle.request.db
    query = db.Select(sets='sessions', where='session_id = ?')
    db.query(query, bottle.request.session.id)
    session_data = db.result

    assert session_data['data'] == '{}'
    assert session_data['session_id'] == bottle.request.session.id
    assert isinstance(session_data['expires'], datetime.datetime)

    callback.assert_called_once_with('test')

    set_cookie.assert_called_once_with(cookie_name,
                                       bottle.request.session.id,
                                       path='/',
                                       secret=secret,
                                       max_age=lifetime)


def assert_session_count_is(expected):
    db = bottle.request.db
    query = db.Select('COUNT(*) as count', sets='sessions')
    db.query(query)
    session_count = db.result.count
    assert session_count == expected


@mock.patch('bottle.response.set_cookie')
@transaction_test
def test_use_existing_session(set_cookie):
    cookie_name = 'session_cookie'
    lifetime = 10
    secret = 'mischief managed'

    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires_in = datetime.timedelta(seconds=lifetime)
    expires = datetime.datetime.utcnow() + expires_in
    session_data = {'session_id': session_id,
                    'data': json.dumps(data),
                    'expires': expires}

    db = bottle.request.db
    query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
    db.execute(query, session_data)

    bottle.request.get_cookie.return_value = session_id

    callback = mock.Mock(__name__='callback')
    plugin = sessions.session_plugin(cookie_name=cookie_name,
                                     lifetime=10,
                                     secret=secret)
    wrapped = plugin(callback)
    wrapped('test')

    assert_session_count_is(1)

    assert bottle.request.session.data == data
    assert bottle.request.session.id == session_id
    assert bottle.request.session.expires == expires

    callback.assert_called_once_with('test')

    set_cookie.assert_called_once_with(cookie_name,
                                       bottle.request.session.id,
                                       path='/',
                                       secret=secret,
                                       max_age=lifetime)


@transaction_test
def test_session_invalid():
    with pytest.raises(sessions.SessionInvalid):
        sessions.Session.fetch(None)

    with pytest.raises(sessions.SessionInvalid):
        sessions.Session.fetch('not valid')


@transaction_test
def test_session_expired():
    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
    session_data = {'session_id': session_id,
                    'data': json.dumps(data),
                    'expires': expires}

    db = bottle.request.db
    query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
    db.execute(query, session_data)

    with pytest.raises(sessions.SessionExpired):
        sessions.Session.fetch(session_id)

    assert_session_count_is(1)
    assert bottle.request.session.id != session_id


@transaction_test
def test_save_session():
    session_id = 'some_session_id'
    data = {'some': 'thing'}
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
    session_data = {'session_id': session_id,
                    'data': json.dumps(data),
                    'expires': expires}

    db = bottle.request.db
    query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
    db.execute(query, session_data)

    s = sessions.Session.fetch(session_id)
    assert s.id == session_id
    assert s.data == data

    s['second'] = 'new'
    s.save()

    assert_session_count_is(1)

    s = sessions.Session.fetch(session_id)
    assert s.id == session_id
    assert s.data == {'some': 'thing', 'second': 'new'}


@transaction_test
def test_regenerate_session():
    s = sessions.Session.create(100)
    s['test'] = 123
    s.save()

    old_session_id = s.id
    old_data = s.data.copy()

    s.regenerate()
    assert s.id != old_session_id
    assert s.data == old_data
    assert_session_count_is(1)
