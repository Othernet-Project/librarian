from datetime import datetime
from os.path import basename, dirname, splitext
from StringIO import StringIO

from bottle import static_file
from fdsend import send_file
from streamline import RouteBase

from ..core.contrib.system.version import get_base_version
from ..data.diagnostics import generate_report


class SendAppLog(RouteBase):

    @property
    def path(self):
        return '/' + basename(self.config['logging.output'])

    def get(self):
        log_path = self.config['logging.output']
        version = get_base_version(self.config) or ''
        log_dir = dirname(log_path)
        filename = basename(log_path)
        (name, ext) = splitext(filename)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        params = dict(name=name, version=version, timestamp=timestamp, ext=ext)
        new_filename = '{name}_{version}_{timestamp}{ext}'.format(**params)
        return static_file(filename, root=log_dir, download=new_filename)


class SendDiag(RouteBase):
    path = '/syslog'

    def get(self):
        platform = self.config['platform.name']
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        diag_file_name = 'diags_{}_{}.log.txt'.format(platform, timestamp)
        # gather log file paths that should be present in the report
        syslog_path = self.config['logging.syslog']
        log_path = self.config['logging.output']
        fsal_path = self.config['logging.fsal_log']
        ondd_socket = self.config.get('ondd.socket')
        # prepare diag report from the gathered log files
        diag_data = generate_report(syslog_path,
                                    log_path,
                                    fsal_path,
                                    ondd_socket)
        return send_file(StringIO(diag_data),
                         filename=diag_file_name,
                         ctype='text/plain',
                         attachment=True,
                         charset='utf-8')
