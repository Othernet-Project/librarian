from .setup import Setup


def initialize(supervisor):
    # install app-wide access to setup parameters
    supervisor.exts.setup = Setup(supervisor.config['setup.file'])
    # merge setup parameters into app config
    supervisor.config.update(dict(supervisor.exts.setup.items()))
