import mock

import librarian.routes.diskspace as mod


# ConsolidateState tests


@mock.patch.object(mod.storage, 'get_consolidate_status')
@mock.patch.object(mod.ConsolidateState, 'request')
def test_consolidate_state_get(request, get_consolidate_status):
    route = mod.ConsolidateState()
    assert route.get() == dict(active=get_consolidate_status.return_value)


# Notifier tests


@mock.patch.object(mod, 'exts')
def test_notifier_clear(exts):
    notifier = mod.Notifier()
    notifier.clear()
    args = ('consolidate_storage', exts.databases.notifications)
    exts.notifications.delete_by_category.assert_called_once_with(*args)


@mock.patch.object(mod, 'exts')
def test_notifier_notify(exts):
    notifier = mod.Notifier()
    notifier.notify('some msg', 'some priority')
    exts.notifications.send.assert_called_once_with(
        'some msg',
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        priority='some priority',
        db=exts.databases.notifications
    )


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Notifier, 'notify')
def test_notifier_success(notify, exts):
    notifier = mod.Notifier()
    dest = mock.Mock()
    dest.humanized_name = 'my storage'
    dest.id = 'abcd'
    notifier.success(dest)
    template = mod.Notifier.messages['success']
    msg = template.format(storage_name=dest.humanized_name)
    notify.assert_called_once_with(msg, mod.exts.notifications.NORMAL)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Notifier, 'notify')
def test_notifier_failure(notify, exts):
    notifier = mod.Notifier()
    dest = mock.Mock()
    dest.humanized_name = 'my storage'
    dest.id = 'abcd'
    notifier.failure(dest)
    template = mod.Notifier.messages['failure']
    msg = template.format(storage_name=dest.humanized_name)
    notify.assert_called_once_with(msg, mod.exts.notifications.URGENT)


@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Notifier, 'notify')
def test_notifier_partial(notify, exts):
    notifier = mod.Notifier()
    dest = mock.Mock()
    dest.humanized_name = 'my storage'
    dest.id = 'abcd'
    notifier.partial(dest)
    template = mod.Notifier.messages['partial']
    msg = template.format(storage_name=dest.humanized_name)
    notify.assert_called_once_with(msg, mod.exts.notifications.URGENT)


# Consolidate tests


@mock.patch.object(mod, 'storage')
@mock.patch.object(mod.Consolidate, 'request')
def test_consolidate_get_context(request, storage):
    request.params = {'storage_id': 'abcd'}
    route = mod.Consolidate()
    exp = dict(storages=storage.get_content_storages.return_value,
               active_storage_id=storage.get_consolidate_status.return_value,
               target_id='abcd')
    ret = route.get_context()
    for (key, value) in exp.items():
        assert ret[key] == value

    storage.get_content_storages.assert_called_once_with()
    storage.get_consolidate_status.assert_called_once_with()


@mock.patch.object(mod, 'storage')
@mock.patch.object(mod, 'exts')
@mock.patch.object(mod.Consolidate, 'request')
def test_consolidate_schedule_task(request, exts, storage):
    route = mod.Consolidate()
    route.form = mock.MagicMock()
    route.schedule_task()
    dest_id = route.form.processed_data['storage_id']
    storages = route.form.processed_data['storages']
    # make sure task is scheduled with correct parameters
    args = (dest_id,
            route.notifier.clear,
            route.notifier.success,
            route.notifier.failure,
            route.notifier.partial)
    exts.tasks.schedule.assert_called_once_with(storages.move_content_to,
                                                args=args)
    # take care of the flag
    storage.mark_consolidate_started.assert_called_once_with(dest_id)


@mock.patch.object(mod, '_')
@mock.patch.object(mod.Consolidate, 'schedule_task')
@mock.patch.object(mod.Consolidate, 'request')
def test_consolidate_form_valid_xhr(request, schedule_task, gettext):
    request.is_xhr = True
    route = mod.Consolidate()
    route.form = mock.MagicMock()
    ret = route.form_valid()
    assert 'message' in ret
    schedule_task.assert_called_once_with()


@mock.patch.object(mod, '_')
@mock.patch.object(mod.Consolidate, 'template_func')
@mock.patch.object(mod.Consolidate, 'schedule_task')
@mock.patch.object(mod.Consolidate, 'request')
def test_consolidate_form_valid(request, schedule_task, gettext, template):
    request.is_xhr = False
    route = mod.Consolidate()
    route.form = mock.MagicMock()
    ret = route.form_valid()
    assert isinstance(ret, mod.Consolidate.HTTPResponse)
    schedule_task.assert_called_once_with()
