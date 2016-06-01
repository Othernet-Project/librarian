import pprint

from ...exceptions import EarlyExit
from ...exts import ext_container as exts
from .version import get_version


class DebugFlag(object):
    name = 'debug'
    flags = '--debug'
    kwargs = {
        'action': 'store_true',
        'help': 'enable debugging'
    }

    def run(self, args):
        exts.config['app.debug'] = args.config


class ConfigPath(object):
    name = 'config'
    flags = '--conf'
    kwargs = {
        'metavar': 'PATH',
        'default': 'config.ini',
        'help': 'path to configuration file'
    }


class DebugConfigCommand(object):
    name = 'debug_conf'
    flags = '--debug-conf'
    kwargs = {
        'action': 'store_true',
        'help': 'print out the configuration in use and exit'
    }

    def run(self, args):
        if not args.debug_conf:
            return

        print('Configuration file path: %s' % exts.config['config_path'])
        pprint.pprint(exts.config, indent=4)
        raise EarlyExit()


class DisplayVersionCommand(object):
    name = 'version'
    flags = '--version'
    kwargs = {
        'action': 'store_true',
        'help': 'print out version number and exit'
    }

    def run(self, args):
        if not args.version:
            return

        print('ver', id(exts))
        ver = get_version(exts.config)
        print('v{}'.format(ver))
        raise EarlyExit()
