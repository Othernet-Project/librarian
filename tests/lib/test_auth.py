import bottle
import mock
import pytest

from librarian.lib import auth, session

from .base import transaction_test


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


@transaction_test
def test_login_user_success():
    bottle.request.session = session.Session.create(300)

    username = 'mike'
    password = 'ekim'
    auth.create_user(username, password)
    assert auth.login_user(username, password)
    assert bottle.request.session['user']['username'] == username


@transaction_test
def test_login_user_invalid_password():
    bottle.request.session = session.Session.create(300)

    username = 'mike'
    password = 'ekim'
    auth.create_user(username, password)
    assert auth.login_user(username, 'invalid') is False
    assert bottle.request.session.get('user') is None


@transaction_test
def test_login_user_invalid_username():
    bottle.request.session = session.Session.create(300)

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
