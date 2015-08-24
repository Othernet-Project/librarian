import bottle

from .handlers import rebuild_assets
from .static import Assets


def component_loaded(supervisor, component, config):
    static_path = config.pop('assets.directory', None)
    static_url = config.pop('assets.url', None)
    if static_path:
        supervisor.config.setdefault('sources', [])
        supervisor.config['assets.sources'].append((static_path, static_url))


def init_begin(supervisor):
    instance = Assets.from_config(supervisor.config)
    supervisor.exts.assets = bottle.BaseTemplate.defaults['assets'] = instance
    supervisor.exts.commands.register('assets',
                                      rebuild_assets,
                                      '--assets',
                                      action='store_true',
                                      help='rebuild static assets')
