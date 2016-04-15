import mock

import librarian.routes.logs as mod


@mock.patch.object(mod.SendAppLog, 'request')
def test_send_app_log_path(request):
    request.app.config = {'logging.output': '/path/to/logfile.log'}
    route = mod.SendAppLog()
    assert route.path == '/logfile.log'


@mock.patch.object(mod, 'datetime')
@mock.patch.object(mod, 'get_base_version')
@mock.patch.object(mod, 'static_file')
@mock.patch.object(mod.SendAppLog, 'request')
def test_send_app_log_get(request, static_file, get_base_version, datetime):
    request.app.config = {'logging.output': '/path/to/logfile.log'}
    route = mod.SendAppLog()
    mocked_dt = mock.Mock()
    mocked_dt.strftime.return_value = 'timestamp'
    datetime.now.return_value = mocked_dt
    get_base_version.return_value = '1.0'
    assert route.get() == static_file.return_value
    static_file.assert_called_once_with('logfile.log',
                                        root='/path/to',
                                        download='logfile_1.0_timestamp.log')


@mock.patch.object(mod, 'generate_report')
@mock.patch.object(mod, 'StringIO')
@mock.patch.object(mod, 'datetime')
@mock.patch.object(mod, 'send_file')
@mock.patch.object(mod.SendDiag, 'request')
def test_send_diag_get(request, send_file, datetime, StringIO,
                       generate_report):
    request.app.config = {'platform.name': 'test',
                          'logging.syslog': '/var/log/messages',
                          'logging.output': '/path/to/logfile.log',
                          'logging.fsal_log': '/path/to/fsal.log',
                          'ondd.socket': '/tmp/ondd.ctrl'}
    mocked_dt = mock.Mock()
    mocked_dt.strftime.return_value = 'timestamp'
    datetime.now.return_value = mocked_dt
    route = mod.SendDiag()
    assert route.get() == send_file.return_value
    send_file.assert_called_once_with(StringIO.return_value,
                                      filename='diags_test_timestamp.log.txt',
                                      ctype='text/plain',
                                      attachment=True,
                                      charset='utf-8')
    StringIO.assert_called_once_with(generate_report.return_value)
    generate_report.assert_called_once_with('/var/log/messages',
                                            '/path/to/logfile.log',
                                            '/path/to/fsal.log',
                                            '/tmp/ondd.ctrl')
