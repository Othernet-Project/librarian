from .defaults import install_default_commands
from .registry import CommandLineHandler


EXPORTS = {
    'initialize': {
        'depends_on': ['librarian_core.contrib.system.hooks.initialize']
    },
    'init_complete': {}
}


def initialize(supervisor):
    supervisor.exts.commands = CommandLineHandler(supervisor)
    install_default_commands(supervisor)


def init_complete(supervisor):
    supervisor.config['args'] = supervisor.exts.commands.handle()
