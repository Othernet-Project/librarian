import os

from .registry import CommandLineHandler


def init_begin(supervisor):
    supervisor.exts.commands = CommandLineHandler(supervisor)
    default_path = os.path.join(supervisor.config['root'],
                                supervisor.DEFAULT_CONFIG_FILENAME)
    supervisor.exts.commands.register('config',
                                      None,
                                      '--conf',
                                      metavar='PATH',
                                      default=default_path,
                                      help='path to configuration file')


def init_complete(supervisor):
    supervisor.config['args'] = supervisor.exts.commands.handle()
