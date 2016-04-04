import datetime

import mock
import pytest

from librarian_notifications import notifications as mod


class TestNotification(object):

    @mock.patch.object(mod, 'datetime')
    @mock.patch.object(mod.Notification, 'save')
    @mock.patch.object(mod.Notification, 'calc_expiry')
    @mock.patch.object(mod.Notification, 'generate_unique_id')
    @mock.patch.object(mod.Notification, '__init__')
    def test_send(self, init_func, generate_unique_id, calc_expiry, save,
                  datetime):
        generate_unique_id.return_value = 'unique id'
        calc_expiry.return_value = 'tomorrow'
        datetime.datetime.now.return_value = 'now'
        init_func.return_value = None
        db = mock.Mock()
        mod.Notification.send('content added',
                              category='content',
                              icon='notify-class',
                              priority=mod.Notification.URGENT,
                              expiration=15,
                              dismissable=False,
                              groupable=False,
                              user='username',
                              group='groupname',
                              db=db)

        init_func.assert_called_once_with(category='content',
                                          notification_id='unique id',
                                          read_at=None,
                                          created_at='now',
                                          expires_at='tomorrow',
                                          dismissable=False,
                                          groupable=False,
                                          priority=1,
                                          user='username',
                                          message='content added',
                                          icon='notify-class',
                                          db=db)
        calc_expiry.assert_called_once_with(15)
        save.assert_called_once_with()

    @mock.patch.object(mod, 'datetime')
    @mock.patch.object(mod.Notification, 'save')
    @mock.patch.object(mod.Notification, 'calc_expiry')
    @mock.patch.object(mod.Notification, 'generate_unique_id')
    @mock.patch.object(mod.Notification, '__init__')
    def test_send_callback(self, init_func, generate_unique_id, calc_expiry,
                           save, datetime):
        callback = mock.Mock()
        mod.Notification.on_send(callback)

        generate_unique_id.return_value = 'unique id'
        calc_expiry.return_value = 'tomorrow'
        datetime.datetime.now.return_value = 'now'
        init_func.return_value = None
        db = mock.Mock()
        inst = mod.Notification.send('content added',
                                     category='content',
                                     icon='notify-class',
                                     priority=mod.Notification.URGENT,
                                     expiration=15,
                                     dismissable=False,
                                     user='username',
                                     group='groupname',
                                     db=db)
        callback.assert_called_once_with(inst)

    def test_has_expired(self):
        notification = mod.Notification('id',
                                        'msg',
                                        'created_at',
                                        db=mock.Mock())
        assert not notification.has_expired

        expires_at = datetime.datetime.now() + datetime.timedelta(days=1)
        notification = mod.Notification('id',
                                        'msg',
                                        'created_at',
                                        expires_at=expires_at,
                                        db=mock.Mock())
        assert not notification.has_expired

        expires_at = datetime.datetime.now() - datetime.timedelta(days=1)
        notification = mod.Notification('id',
                                        'msg',
                                        'created_at',
                                        expires_at=expires_at,
                                        db=mock.Mock())
        assert notification.has_expired

    def test_is_shared(self):
        notification = mod.Notification('id',
                                        'msg',
                                        'created_at',
                                        db=mock.Mock())
        assert notification.is_shared

        notification = mod.Notification('id',
                                        'msg',
                                        'created_at',
                                        user='ted',
                                        db=mock.Mock())
        assert not notification.is_shared

    @mock.patch.object(mod.Notification, 'is_shared')
    def test_read_at_private(self, is_shared):
        is_shared.__get__ = mock.Mock(return_value=False)
        notification = mod.Notification('id',
                                        'msg',
                                        'today',
                                        read_at='now',
                                        db=mock.Mock())
        assert notification.read_at == 'now'

    @mock.patch.object(mod, 'request')
    @mock.patch.object(mod.Notification, 'is_shared')
    def test_read_at_shared(self, is_shared, request):
        is_shared.__get__ = mock.Mock(return_value=True)
        request.user.options.get.return_value = {'unique_id': 'sometime'}
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        assert notification.read_at == 'sometime'

    @mock.patch.object(mod.Notification, 'read_at')
    def test_is_read_true(self, read_at):
        read_at.__get__ = mock.Mock(return_value='now')
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        assert notification.is_read

    @mock.patch.object(mod.Notification, 'read_at')
    def test_is_read_false(self, read_at):
        read_at.__get__ = mock.Mock(return_value=None)
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        assert not notification.is_read

    @mock.patch.object(mod, 'request')
    def test__mark_shared_read_creates(self, request):
        request.user.options = {}
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        notification._mark_shared_read('now')
        assert request.user.options == {'notifications': {'unique_id': 'now'}}

    @mock.patch.object(mod, 'request')
    def test__mark_shared_read_updates(self, request):
        request.user.options = {'notifications': {'previous': 'yesterday'}}
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        notification._mark_shared_read('now')
        expected = {'notifications': {'previous': 'yesterday',
                                      'unique_id': 'now'}}
        assert request.user.options == expected

    @mock.patch.object(mod, 'request')
    def test__mark_private_read(self, request):
        db = mock.Mock()
        notification = mod.Notification('unique_id', 'msg', 'today', db=db)
        notification._mark_private_read('now')
        db.query.assert_called_once_with(db.Update.return_value,
                                         notification_id='unique_id',
                                         read_at='now')

    @mock.patch.object(mod.Notification, '_mark_private_read')
    @mock.patch.object(mod.Notification, '_mark_shared_read')
    @mock.patch.object(mod.Notification, 'is_read')
    def test_mark_read_already_read(self, is_read, _mark_shared_read,
                                    _mark_private_read):
        is_read.__get__ = mock.Mock(return_value=True)
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        notification.mark_read()
        assert not _mark_private_read.called
        assert not _mark_shared_read.called

    @mock.patch.object(mod, 'datetime')
    @mock.patch.object(mod.Notification, '_mark_shared_read')
    @mock.patch.object(mod.Notification, 'is_shared')
    @mock.patch.object(mod.Notification, 'is_read')
    def test_mark_read_shared(self, is_read, is_shared, _mark_shared_read,
                              datetime):
        is_read.__get__ = mock.Mock(return_value=False)
        is_shared.__get__ = mock.Mock(return_value=True)
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        notification.mark_read('now')
        _mark_shared_read.assert_called_once_with('now')

        _mark_shared_read.reset_mock()

        datetime.datetime.now.return_value = 'proper date'
        notification.mark_read()
        _mark_shared_read.assert_called_once_with('proper date')

    @mock.patch.object(mod, 'datetime')
    @mock.patch.object(mod.Notification, '_mark_private_read')
    @mock.patch.object(mod.Notification, 'is_shared')
    @mock.patch.object(mod.Notification, 'is_read')
    def test_mark_read_private(self, is_read, is_shared, _mark_private_read,
                               datetime):
        is_read.__get__ = mock.Mock(return_value=False)
        is_shared.__get__ = mock.Mock(return_value=False)
        notification = mod.Notification('unique_id',
                                        'msg',
                                        'today',
                                        db=mock.Mock())
        notification.mark_read('now')
        _mark_private_read.assert_called_once_with('now')

        _mark_private_read.reset_mock()

        datetime.datetime.now.return_value = 'proper date'
        notification.mark_read()
        _mark_private_read.assert_called_once_with('proper date')

    def test_save(self):
        db = mock.Mock()
        notification = mod.Notification('unique_id', 'msg', 'today', db=db)
        notification.save()
        db.query.assert_called_once_with(
            db.Replace.return_value,
            category=None,
            notification_id='unique_id',
            read_at=None,
            created_at='today',
            expires_at=None,
            dismissable=True,
            groupable=True,
            priority=mod.Notification.NORMAL,
            user=None,
            message='msg',
            icon=None
        )

    def test_delete(self):
        db = mock.Mock()
        notification = mod.Notification('unique_id', 'msg', 'today', db=db)
        notification.delete()
        db.query.assert_called_once_with(db.Delete.return_value, 'unique_id')

    def test_generate_unique_id(self):
        uid = mod.Notification.generate_unique_id()
        assert isinstance(uid, str)
        assert len(uid) == 32

    def test_calc_expiry(self):
        assert mod.Notification.calc_expiry(0) is None
        assert isinstance(mod.Notification.calc_expiry(10), datetime.datetime)


class TestNotificationGroup(object):

    @mock.patch.object(mod, 'request')
    def test_notification_attrs(self, request):
        notification = mod.Notification('uid', 'msg', 'now', db=mock.Mock())
        group = mod.NotificationGroup([notification])
        for attr in mod.NotificationGroup.proxied_attrs:
            assert getattr(group, attr) == getattr(notification, attr)

    def test_empty_group(self):
        group = mod.NotificationGroup()
        with pytest.raises(ValueError):
            group.category

    def test_count(self):
        notification = mod.Notification('uid', 'msg', 'now', db=mock.Mock())
        notification2 = mod.Notification('uid2', 'msg', 'now', db=mock.Mock())
        group = mod.NotificationGroup([notification, notification2])
        assert group.count == 2

    def test_add(self):
        notification = mod.Notification('uid', 'msg', 'now', db=mock.Mock())
        group = mod.NotificationGroup()
        group.add(notification)
        assert group.notifications == [notification]

    def test_is_similar_default(self):
        notification = mod.Notification('uid',
                                        'msg',
                                        'now',
                                        category='content',
                                        read_at='now',
                                        user='joe',
                                        db=mock.Mock())
        group = mod.NotificationGroup([notification])
        similar = mod.Notification('uid',
                                   'msg',
                                   'now',
                                   category='content',
                                   read_at='now',
                                   user='joe',
                                   db=mock.Mock())
        different1 = mod.Notification('uid',
                                      'msg',
                                      'now',
                                      category='other',
                                      read_at='now',
                                      user='joe',
                                      db=mock.Mock())
        different2 = mod.Notification('uid',
                                      'msg',
                                      'now',
                                      category='content',
                                      read_at='yesterday',
                                      user='joe',
                                      db=mock.Mock())
        assert group.is_similar(similar, attrs=('category', 'read_at'))
        assert not group.is_similar(different1, attrs=('category', 'read_at'))
        assert not group.is_similar(different2, attrs=('category', 'read_at'))

    def test_group_by(self):
        notifications = []
        fixtures = [dict(category='content'),
                    dict(category='content'),
                    dict(category='content', groupable=False),
                    dict(),
                    dict(),
                    dict(category='alarm'),
                    dict(category='alarm')]
        for idx, options in enumerate(fixtures):
            notifications.append(mod.Notification('uid' + str(idx),
                                                  'msg',
                                                  'now',
                                                  user='joe',
                                                  db=mock.Mock(),
                                                  **options))
        groups = mod.NotificationGroup.group_by(iter(notifications),
                                                by=('category', 'read_at'))
        assert len(groups) == 5
        assert groups[0].count == 2  # content
        assert groups[1].count == 1  # content - not groupable
        assert groups[2].count == 1  # empty
        assert groups[3].count == 1  # empty
        assert groups[4].count == 2  # alarm
