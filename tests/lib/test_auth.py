import datetime
import json

import bottle
import mock
import pytest

from librarian.app import in_pkg
from librarian.lib import auth, squery
from librarian.utils import migrations


def transaction_test(func):
    def _transaction_test(*args, **kwargs):
        with mock.patch('bottle.request') as bottle_request:
            conn = squery.Connection()
            db = squery.Database(conn)
            config = {'content.contentdir': '/tmp'}
            migrations.migrate(db,
                               in_pkg('migrations'),
                               'librarian.migrations',
                               config)
            bottle_request.db = db

            return func(*args, **kwargs)

    return _transaction_test


def test_password_encryption():
    encrypted = auth.encrypt_password('super secure')
    assert auth.is_valid_password('super secure', encrypted)


@transaction_test
def test_create_user():
    username = 'mike'
    password = 'mikepassword'

    auth.create_user(username, password)

    db = bottle.request.db
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    user = db.result

    assert user.username == username
    assert user.is_superuser == 0
    assert auth.is_valid_password(password, user.password)


@transaction_test
def test_create_user_already_exists():
    username = 'mike'
    password = 'mikepassword'

    auth.create_user(username, password)
    with pytest.raises(auth.UserAlreadyExists):
        auth.create_user(username, password)


@transaction_test
def test_create_user_invalid_credentials():
    with pytest.raises(auth.InvalidUserCredentials):
        auth.create_user('', '')

    with pytest.raises(auth.InvalidUserCredentials):
        auth.create_user(None, None)

    with pytest.raises(auth.InvalidUserCredentials):
        auth.create_user('mike', '')

    with pytest.raises(auth.InvalidUserCredentials):
        auth.create_user('', 'somepassword')


@mock.patch('bottle.redirect')
@mock.patch('bottle.request')
def test_login_required_not_logged_in(bottle_request, bottle_redirect):
    mock_controller = mock.Mock(__name__='controller')
    protected = auth.login_required()(mock_controller)

    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.session.get.return_value = None

    protected()

    bottle_redirect.assert_called_once_with('/login/?next=%2Fsomewhere%2F')
    assert mock_controller.called is False


@mock.patch('bottle.template')
@mock.patch('bottle.request')
def test_login_required_forbidden(bottle_request, bottle_template):
    mock_controller = mock.Mock(__name__='controller')
    protected = auth.login_required(superuser_only=True)(mock_controller)

    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.session.get.return_value = {'is_superuser': False}

    protected()

    bottle_template.assert_called_once_with('403')
    assert mock_controller.called is False


@mock.patch('bottle.request')
def test_login_required_success_superuser(bottle_request):
    mock_controller = mock.Mock(__name__='controller')
    protected = auth.login_required(superuser_only=True)(mock_controller)

    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.session.get.return_value = {'is_superuser': True}

    protected('test')

    mock_controller.assert_called_once_with('test')


@mock.patch('bottle.request')
def test_login_required_success_normaluser(bottle_request):
    mock_controller = mock.Mock(__name__='controller')
    protected = auth.login_required()(mock_controller)

    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.session.get.return_value = {'is_superuser': False}

    protected('test')

    mock_controller.assert_called_once_with('test')


@mock.patch('bottle.response.set_cookie')
@transaction_test
def test_create_new_session(set_cookie):
    bottle.request.get_cookie.return_value = None

    cookie_name = 'session_cookie'
    lifetime = 10
    secret = 'mischief managed'

    callback = mock.Mock(__name__='callback')
    plugin = auth.session_plugin(cookie_name=cookie_name,
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
    plugin = auth.session_plugin(cookie_name=cookie_name,
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
    with pytest.raises(auth.SessionInvalid):
        auth.Session.fetch(None)

    with pytest.raises(auth.SessionInvalid):
        auth.Session.fetch('not valid')


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

    with pytest.raises(auth.SessionExpired):
        auth.Session.fetch(session_id)

    assert_session_count_is(0)


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

    session = auth.Session.fetch(session_id)
    assert session.id == session_id
    assert session.data == data

    session['second'] = 'new'
    session.save()

    assert_session_count_is(1)

    session = auth.Session.fetch(session_id)
    assert session.id == session_id
    assert session.data == {'some': 'thing', 'second': 'new'}


@transaction_test
def test_login_user_success():
    bottle.request.session = auth.Session.create(300)

    username = 'mike'
    password = 'ekim'
    auth.create_user(username, password)
    assert auth.login_user(username, password)
    assert bottle.request.session['user']['username'] == username


@transaction_test
def test_login_user_invalid_password():
    bottle.request.session = auth.Session.create(300)

    username = 'mike'
    password = 'ekim'
    auth.create_user(username, password)
    assert auth.login_user(username, 'invalid') is False
    assert bottle.request.session.get('user') is None


@transaction_test
def test_login_user_invalid_username():
    bottle.request.session = auth.Session.create(300)

    username = 'mike'
    password = 'ekim'
    auth.create_user(username, password)
    assert auth.login_user('missing', 'invalid') is False
    assert bottle.request.session.get('user') is None


def test_get_redirect_path():
    result = auth.get_redirect_path('/login/', '/original/')
    assert result == '/login/?next=%2Foriginal%2F'

    result = auth.get_redirect_path('/login/',
                                    '/original/',
                                    next_param_name='go')
    assert result == '/login/?go=%2Foriginal%2F'

    result = auth.get_redirect_path('/login/?abc=123', '/original/?imok=1')
    assert result == '/login/?abc=123&next=%2Foriginal%2F%3Fimok%3D1'
