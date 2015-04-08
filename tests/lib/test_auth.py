import datetime
import json

import mock
import pytest

from librarian.lib import sessions, auth as mod

from .base import transaction_test


MOD = mod.__name__


def assert_session_count_is(expected):
    db = mod.request.db.sessions
    query = db.Select('COUNT(*) as count', sets='sessions')
    db.query(query)
    session_count = db.result.count
    assert session_count == expected


def prepare_session(func):
    def _prepare_session(*args, **kwargs):
        session_id = 'some_session_id'
        data = {'some': 'thing'}
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)

        db = mod.request.db.sessions
        query = db.Insert('sessions', cols=('session_id', 'data', 'expires'))
        db.execute(query, {'session_id': session_id,
                           'data': json.dumps(data),
                           'expires': expires})

        mod.request.session = sessions.Session(session_id, data, expires)
        mod.request.user = mod.User()

        return func(*args, **kwargs)
    return _prepare_session


def test_password_encryption():
    encrypted = mod.encrypt_password('super secure')
    assert mod.is_valid_password('super secure', encrypted)


@transaction_test(MOD + '.request')
def test_create_user():
    username = 'mike'
    password = 'mikepassword'

    mod.create_user(username, password)

    db = mod.request.db.sessions
    query = db.Select(sets='users', where='username = ?')
    db.query(query, username)
    user = db.result

    assert user.username == username
    assert user.is_superuser == 0
    assert mod.is_valid_password(password, user.password)


@transaction_test(MOD + '.request')
def test_create_user_already_exists():
    username = 'mike'
    password = 'mikepassword'

    mod.create_user(username, password)
    with pytest.raises(mod.UserAlreadyExists):
        mod.create_user(username, password)


@transaction_test(MOD + '.request')
def test_create_user_invalid_credentials():
    with pytest.raises(mod.InvalidUserCredentials):
        mod.create_user('', '')

    with pytest.raises(mod.InvalidUserCredentials):
        mod.create_user(None, None)

    with pytest.raises(mod.InvalidUserCredentials):
        mod.create_user('mike', '')

    with pytest.raises(mod.InvalidUserCredentials):
        mod.create_user('', 'somepassword')


@mock.patch(MOD + '.redirect')
@mock.patch(MOD + '.request')
def test_login_required_no_auth(bottle_request, bottle_redirect):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required()(mock_controller)

    bottle_request.no_auth = True
    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.user.is_authenticated = False

    protected('test')

    mock_controller.assert_called_once_with('test')


@mock.patch(MOD + '.redirect')
@mock.patch(MOD + '.request')
def test_login_required_not_logged_in(bottle_request, bottle_redirect):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required()(mock_controller)

    bottle_request.no_auth = False
    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.user.is_authenticated = False

    protected()

    bottle_redirect.assert_called_once_with('/login/?next=%2Fsomewhere%2F')
    assert mock_controller.called is False


@mock.patch(MOD + '.redirect')
@mock.patch(MOD + '.request')
def test_login_required_not_logged_in_next_to(bottle_request, bottle_redirect):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required(next_to='/go-here/')(mock_controller)

    bottle_request.no_auth = False
    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.user.is_authenticated = False

    protected()

    bottle_redirect.assert_called_once_with('/login/?next=%2Fgo-here%2F')
    assert mock_controller.called is False


@mock.patch(MOD + '.abort')
@mock.patch(MOD + '.request')
def test_login_required_forbidden(bottle_request, bottle_abort):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required(superuser_only=True)(mock_controller)

    bottle_request.no_auth = False
    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.user.is_authenticated = True
    bottle_request.user.is_superuser = False

    protected()

    bottle_abort.assert_called_once_with(403)
    assert mock_controller.called is False


@mock.patch(MOD + '.request')
def test_login_required_success_superuser(bottle_request):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required(superuser_only=True)(mock_controller)

    bottle_request.no_auth = False
    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.user.is_authenticated = True
    bottle_request.user.is_superuser = True

    protected('test')

    mock_controller.assert_called_once_with('test')


@mock.patch(MOD + '.request')
def test_login_required_success_normaluser(bottle_request):
    mock_controller = mock.Mock(__name__='controller')
    protected = mod.login_required()(mock_controller)

    bottle_request.fullpath = '/somewhere/'
    bottle_request.query_string = ''
    bottle_request.session.get.return_value = {'is_superuser': False}

    protected('test')

    mock_controller.assert_called_once_with('test')


@transaction_test([MOD + '.request', sessions.__name__ + '.request'])
@prepare_session
def test_login_user_success():
    old_session_id = mod.request.session.id
    username = 'mike'
    password = 'ekim'
    mod.create_user(username, password)
    assert mod.login_user(username, password)
    assert mod.request.session.id != old_session_id
    assert mod.request.user.is_authenticated
    assert mod.request.user.username == username
    assert mod.request.user.options.to_native() == {}


@transaction_test(MOD + '.request')
@prepare_session
def test_login_user_invalid_password():
    username = 'mike'
    password = 'ekim'
    mod.create_user(username, password)
    assert mod.login_user(username, 'invalid') is False
    assert not mod.request.user.is_authenticated


@transaction_test(MOD + '.request')
@prepare_session
def test_login_user_invalid_username():
    username = 'mike'
    password = 'ekim'
    mod.create_user(username, password)
    assert mod.login_user('missing', 'invalid') is False
    assert not mod.request.user.is_authenticated


@transaction_test([MOD + '.request', sessions.__name__ + '.request'])
@prepare_session
def test_logout():
    old_session_id = mod.request.session.id
    username = 'mike'
    password = 'ekim'
    mod.create_user(username, password)

    assert mod.login_user(username, password)
    new_session_id = mod.request.session.id
    assert new_session_id != old_session_id
    assert mod.request.user.is_authenticated
    assert mod.request.user.username == username
    assert_session_count_is(1)

    mod.request.user.logout()

    assert mod.request.session.id != new_session_id
    assert_session_count_is(0)


def test_get_redirect_path():
    result = mod.get_redirect_path('/login/', '/original/')
    assert result == '/login/?next=%2Foriginal%2F'

    result = mod.get_redirect_path('/login/',
                                   '/original/',
                                   next_param_name='go')
    assert result == '/login/?go=%2Foriginal%2F'

    result = mod.get_redirect_path('/login/?abc=123', '/original/?imok=1')
    assert result == '/login/?abc=123&next=%2Foriginal%2F%3Fimok%3D1'
