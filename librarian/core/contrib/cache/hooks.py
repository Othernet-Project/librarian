from ...exports import hook
from .helpers import setup


@hook('initialize')
def initialize(supervisor):
    backend = supervisor.config['cache.backend']
    supervisor.exts.cache = setup(backend, supervisor.config)
