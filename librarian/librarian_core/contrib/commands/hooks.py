from .registry import CommandLineHandler


def init_begin(supervisor):
    supervisor.exts.commands = CommandLineHandler(supervisor)


def init_complete(supervisor):
    supervisor.config['args'] = supervisor.exts.commands.handle()
