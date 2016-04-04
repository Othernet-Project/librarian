from .helpers import setup


def initialize(supervisor):
    backend = supervisor.config['cache.backend']
    supervisor.exts.cache = setup(backend, supervisor.config)
