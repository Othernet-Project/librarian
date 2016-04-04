import os
import pprint


def debug_on(arg, supervisor):
    supervisor.config['app.debug'] = arg


def debug_conf(arg, supervisor):
    print('Configuration file path: %s' % supervisor.config_path)
    pprint.pprint(supervisor.config, indent=4)
    raise supervisor.EarlyExit()


def install_default_commands(supervisor):
    default_path = os.path.join(supervisor.config['root'],
                                supervisor.DEFAULT_CONFIG_FILENAME)
    supervisor.exts.commands.register('config',
                                      None,
                                      '--conf',
                                      metavar='PATH',
                                      default=default_path,
                                      help='path to configuration file')
    supervisor.exts.commands.register('debug',
                                      debug_on,
                                      '--debug',
                                      action='store_true',
                                      help='enable debugging')
    supervisor.exts.commands.register('debug_conf',
                                      debug_conf,
                                      '--debug-conf',
                                      action='store_true',
                                      help='print out the configuration in '
                                           'use and exit')
