import datetime
from StringIO import StringIO
from os.path import basename, dirname, splitext

from fdsend import send_file
from bottle import request, static_file
from librarian_core.contrib.system.version import get_base_version

from .diagnostics import generate_report


def send_logfile(log_path):
    version = get_base_version(request.app.config) or ''
    log_dir = dirname(log_path)
    filename = basename(log_path)
    (name, ext) = splitext(filename)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    params = dict(name=name, version=version, timestamp=timestamp, ext=ext)
    new_filename = '{name}_{version}_{timestamp}{ext}'.format(**params)
    return static_file(filename, root=log_dir, download=new_filename)


def send_applog():
    log_path = request.app.config['logging.output']
    return send_logfile(log_path)


def send_diags():
    platform = request.app.config['platform.name']
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    diag_file_name = 'diags_{}_{}.log.txt'.format(platform, timestamp)

    syslog_path = request.app.config['logging.syslog']
    log_path = request.app.config['logging.output']
    fsal_path = request.app.config['logging.fsal_log']
    ondd_socket = request.app.config.get('ondd.socket')

    diag_data = generate_report(syslog_path, log_path, fsal_path, ondd_socket)
    return send_file(StringIO(diag_data),
                     filename=diag_file_name,
                     ctype='text/plain',
                     attachment=True,
                     charset='utf-8')


def routes(config):
    log_name = basename(config['logging.output'])
    opts = dict(unlocked=True)
    return (
        ('sys:applog', send_applog, 'GET', '/{0}'.format(log_name), opts),
        ('sys:syslog', send_diags, 'GET', '/syslog', opts),
    )
