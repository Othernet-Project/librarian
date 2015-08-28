import bottle

from .handlers import rebuild_assets
from .static import Assets


def component_member_loaded(supervisor, member, config):
    supervisor.config.setdefault('assets.sources', {})
    pkg_name = member['pkg_name']
    if pkg_name not in supervisor.config['assets.sources']:
        static_path = config.pop('assets.directory', None)
        static_url = config.pop('assets.url', None)
        if static_path:
            supervisor.config['assets.sources'][pkg_name] = (static_path,
                                                             static_url)


def initialize(supervisor):
    instance = Assets.from_config(supervisor.config)
    supervisor.exts.assets = bottle.BaseTemplate.defaults['assets'] = instance
    supervisor.exts.commands.register('assets',
                                      rebuild_assets,
                                      '--assets',
                                      action='store_true',
                                      help='rebuild static assets')
