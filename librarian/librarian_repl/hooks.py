from .commands import repl


def initialize(supervisor):
    supervisor.exts.commands.register(
        'repl',
        repl,
        '--repl',
        action='store_true',
        help='start interactive shell after servers start'
    )
