from .commands import create_superuser


EXPORTS = {
    'initialize': {
        'depends_on': ['librarian_core.contrib.databases.hooks.initialize']
    }
}


def initialize(supervisor):
    supervisor.exts.commands.register('su',
                                      create_superuser,
                                      '--su',
                                      action='store_true')
    supervisor.exts.commands.register('no_auth',
                                      None,
                                      '--no-auth',
                                      action='store_true',
                                      help='disable authentication')
