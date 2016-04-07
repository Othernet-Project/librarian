import mock

from bottle_utils import csrf

import librarian.utils.route_mixins as mod


# Common test helper


class MockedRouteBase(object):

    def __init__(self, *args, **kwargs):
        # this way all tests will get a separate instance of the mock
        # object when they instantiate their routes, because otherwise
        # a class level mock would carry over state from previous tests
        self.request = mock.Mock()
        self.response = mock.Mock()

    def get(self, *args, **kwargs):
        return None

    def post(self, *args, **kwargs):
        return None

    def get_default_context(self):
        return {'default': 'default'}


# CSRFRouteMixin tests


@mock.patch.object(csrf, 'response')
@mock.patch.object(csrf, 'request')
def test_csrf_route_mixin_get(request, response):
    request.get_cookie.return_value = ''

    class TestRoute(mod.CSRFRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    inst.get()
    assert hasattr(inst.request, 'csrf_token')


@mock.patch.object(csrf, 'abort')
@mock.patch.object(csrf, 'response')
@mock.patch.object(csrf, 'request')
def test_csrf_route_mixin_post(request, response, abort):
    request.get_cookie.return_value = ''

    class TestRoute(mod.CSRFRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    inst.post()
    assert abort.called


# RedirectRouteMixin tests


def test_redirect_route_mixin_get_next_path_found():

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    assert inst.get_next_path() == inst.request.params.get.return_value


def test_redirect_route_mixin_get_next_path_default():

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    inst.request.params = {}
    assert inst.get_next_path() == inst.default_next_path


@mock.patch.object(mod.RedirectRouteMixin, 'get_next_path')
def test_redirect_route_mixin_get_default_context(get_next_path):

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    exp = {'default': 'default',
           inst.next_context_parameter_name: inst.get_next_path.return_value}
    assert inst.get_default_context() == exp
    assert inst.get_next_path.called


@mock.patch.object(mod, 'i18n_path')
@mock.patch.object(mod.RedirectRouteMixin, 'get_next_path')
def test_redirect_route_mixin_get_redirect_url(get_next_path, i18n_path):
    i18n_path.return_value = '/en/some/path/'

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()
    inst.request.url = 'http://localhost/'
    assert inst.get_redirect_url() == 'http://localhost/en/some/path/'
    assert inst.get_next_path.called
    i18n_path.assert_called_with(get_next_path.return_value)


@mock.patch.object(mod.RedirectRouteMixin, 'get_redirect_url')
def test_redirect_route_mixin_perform_redirect_default(get_redirect_url):

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()

    inst.perform_redirect()
    inst.response.set_header.assert_called_with('Location',
                                                get_redirect_url.return_value)
    assert inst.response.status == 303


@mock.patch.object(mod.RedirectRouteMixin, 'get_redirect_url')
def test_redirect_route_mixin_perform_redirect_custom(get_redirect_url):

    class TestRoute(mod.RedirectRouteMixin, MockedRouteBase):
        pass

    inst = TestRoute()

    custom_url = 'outernet.is'
    custom_status = 302
    inst.perform_redirect(custom_url, custom_status)
    inst.response.set_header.assert_called_with('Location', custom_url)
    assert inst.response.status == custom_status
