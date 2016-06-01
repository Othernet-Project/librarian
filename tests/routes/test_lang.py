import mock

import librarian.routes.lang as mod


@mock.patch.object(mod.List, 'request')
def test_list_get(request):
    route = mod.List()
    assert route.get() == {}
