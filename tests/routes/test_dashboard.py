import mock

from ..helpers import strip_wrappers

import librarian.routes.dashboard as mod


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Dashboard, 'request')
def test_dashboard_get(request, exts):
    request.no_auth = True
    route = mod.Dashboard()
    get_fn = strip_wrappers(route.get)
    assert get_fn(route) == {'plugins': exts.dashboard.plugins}
