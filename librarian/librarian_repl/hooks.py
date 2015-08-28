from .repl import repl


def initialize(supervisor):
    supervisor.exts.commands.register(
        'version',
        repl,
        '--repl',
        action='store_true',
        help='start interactive shell after servers start'
    )
