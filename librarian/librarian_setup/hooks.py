from .setup import Setup


def init_begin(supervisor):
    # install app-wide access to setup parameters
    supervisor.exts.setup = Setup(supervisor.config['setup.file'])
    # merge setup parameters into app config
    supervisor.config.update(dict(supervisor.setup.items()))
