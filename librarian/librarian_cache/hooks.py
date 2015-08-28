from .cache import setup


def initialize(supervisor):
    supervisor.exts.cache = setup(backend=supervisor.config['cache.backend'],
                                  timeout=supervisor.config['cache.timeout'],
                                  servers=supervisor.config['cache.servers'])
