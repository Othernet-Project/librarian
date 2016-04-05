import os

import bottle

from .handlers import rebuild_assets, collect_assets
from .static import Assets


EXPORTS = {
    'component_member_loaded': {},
    'initialize': {
        'depends_on': ['librarian.core.contrib.commands.hooks.initialize']
    },
    'init_complete': {
        'required_by': ['librarian.core.contrib.commands.hooks.init_complete']
    }
}

DEFAULT_STATIC_ROOT = 'static'
DEFAULT_STATIC_URL = '/static/'


def component_member_loaded(supervisor, member, config):
    supervisor.config.setdefault('assets.sources', {})
    supervisor.config.setdefault('assets.js_bundles', [])
    supervisor.config.setdefault('assets.css_bundles', [])
    pkg_name = member['pkg_name']
    if pkg_name not in supervisor.config['assets.sources']:
        static_dir = config.pop('assets.directory', DEFAULT_STATIC_ROOT)
        static_path = os.path.join(member['pkg_path'], static_dir)
        static_url = config.pop('assets.url', DEFAULT_STATIC_URL)
        js_bundles = config.pop('assets.js_bundles', [])
        css_bundles = config.pop('assets.css_bundles', [])
        if static_path and os.path.exists(static_path):
            src_pair = (static_path, static_url)
            supervisor.config['assets.sources'][pkg_name] = src_pair
            supervisor.config['assets.js_bundles'].extend(js_bundles)
            supervisor.config['assets.css_bundles'].extend(css_bundles)


def initialize(supervisor):
    supervisor.exts.commands.register('assets',
                                      rebuild_assets,
                                      '--assets',
                                      action='store_true',
                                      help='rebuild static assets')
    supervisor.exts.commands.register('collect',
                                      collect_assets,
                                      '--collect',
                                      action='store_true',
                                      help='collect static assets')


def init_complete(supervisor):
    instance = Assets.from_config(supervisor.config)
    supervisor.exts.assets = bottle.BaseTemplate.defaults['assets'] = instance
