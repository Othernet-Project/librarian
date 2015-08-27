from .commands import display_version


def init_begin(supervisor):
    supervisor.exts.commands.register('version',
                                      display_version,
                                      '--version',
                                      action='store_true',
                                      help='print out version number and exit')
