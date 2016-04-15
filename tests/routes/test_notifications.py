import mock

import librarian.routes.notifications as mod


@mock.patch.object(mod, 'get_notification_groups')
@mock.patch.object(mod.List, 'request')
def test_list_show_form(request, get_notification_groups):
    route = mod.List()
    ret = route.show_form()
    assert ret == {'groups': get_notification_groups.return_value}
    get_notification_groups.assert_called_once_with()


@mock.patch.object(mod, 'utcnow')
@mock.patch.object(mod.List, 'request')
def test_list_mark_read(request, utcnow):
    notifications = [mock.Mock(), mock.Mock(dismissable=False)]
    route = mod.List()
    route.mark_read(notifications)
    notifications[0].mark_read.assert_called_once_with(utcnow.return_value)
    assert not notifications[1].mark_read.called


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.List, 'request')
def test_list_invalidate_cache(request, exts):
    request.session.id = '1'
    route = mod.List()
    route.invalidate_cache()
    calls = [mock.call('notification_group_1'),
             mock.call('notification_count_1')]
    exts.cache.delete.assert_has_calls(calls)


@mock.patch.object(mod, 'get_notifications')
@mock.patch.object(mod, 'NotificationGroup')
@mock.patch.object(mod.List, 'request')
def test_list_get_markable_groups_specific(request, NotificationGroup,
                                           get_notifications):
    route = mod.List()
    route.form = mock.Mock()
    route.form.processed_data = {'notification_id': 'a1'}
    route.form.should_mark_all.return_value = False

    specific = mock.Mock(first_id='a1')
    groups = [mock.Mock(), specific, mock.Mock()]
    NotificationGroup.group_by.return_value = groups

    assert route.get_markable_groups() == [specific]

    route.form.should_mark_all.assert_called_once_with()
    get_notifications.assert_called_once_with()
    NotificationGroup.group_by.assert_called_once_with(
        get_notifications.return_value,
        by=('category', 'read_at')
    )


@mock.patch.object(mod, 'get_notifications')
@mock.patch.object(mod, 'NotificationGroup')
@mock.patch.object(mod.List, 'request')
def test_list_get_markable_groups_all(request, NotificationGroup,
                                      get_notifications):
    route = mod.List()
    route.form = mock.Mock()
    route.form.processed_data = {'notification_id': 'a1'}
    route.form.should_mark_all.return_value = True

    groups = [mock.Mock(), mock.Mock(), mock.Mock()]
    NotificationGroup.group_by.return_value = groups

    assert route.get_markable_groups() == groups

    route.form.should_mark_all.assert_called_once_with()
    get_notifications.assert_called_once_with()
    NotificationGroup.group_by.assert_called_once_with(
        get_notifications.return_value,
        by=('category', 'read_at')
    )


@mock.patch.object(mod.List, 'invalidate_cache')
@mock.patch.object(mod.List, 'mark_read')
@mock.patch.object(mod.List, 'get_markable_groups')
@mock.patch.object(mod.List, 'request')
def test_list_form_valid(request, get_markable_groups, mark_read,
                         invalidate_cache):
    groups = [mock.Mock(is_read=False), mock.Mock(is_read=False), mock.Mock()]
    get_markable_groups.return_value = groups

    route = mod.List()
    assert route.form_valid() == {'groups': [groups[0], groups[1]]}

    calls = [mock.call(grp.notifications) for grp in groups]
    mark_read.assert_has_calls(calls)
    invalidate_cache.assert_called_once_with()
