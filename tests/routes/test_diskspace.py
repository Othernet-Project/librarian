import mock

import librarian.routes.diskspace as mod


@mock.patch.object(mod.storage, 'get_consolidate_status')
@mock.patch.object(mod.ConsolidateState, 'request')
def test_consolidate_state_get(request, get_consolidate_status):
    route = mod.ConsolidateState()
    assert route.get() == dict(active=get_consolidate_status.return_value)
