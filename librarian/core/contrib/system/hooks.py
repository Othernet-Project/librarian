from .commands import display_version
from .routes import error_403, error_404, error_500, error_503


def initialize(supervisor):
    supervisor.app.error(403)(error_403)
    supervisor.app.error(404)(error_404)
    supervisor.app.error(500)(error_500)
    supervisor.app.error(503)(error_503)
    supervisor.exts.commands.register('version',
                                      display_version,
                                      '--version',
                                      action='store_true',
                                      help='print out version number and exit')
