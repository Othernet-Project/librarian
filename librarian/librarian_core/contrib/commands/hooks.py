from .defaults import install_default_commands
from .registry import CommandLineHandler


def init_begin(supervisor):
    supervisor.exts.commands = CommandLineHandler(supervisor)
    install_default_commands(supervisor)


def init_complete(supervisor):
    supervisor.config['args'] = supervisor.exts.commands.handle()
