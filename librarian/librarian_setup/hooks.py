import importlib

from .setup import Setup


def component_member_loaded(supervisor, member, config):
    mod_path = '{0}.setup'.format(member['pkg_name'])
    try:
        importlib.import_module(mod_path)  # they autoregister themselves
    except ImportError:
        pass  # no setup wizard steps in this component


def initialize(supervisor):
    # install app-wide access to setup parameters
    supervisor.exts.setup = Setup(supervisor.config['setup.file'])
    # merge setup parameters into app config
    supervisor.config.update(dict(supervisor.exts.setup.items()))
