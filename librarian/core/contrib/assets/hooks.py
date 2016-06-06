import bottle

from ...exports import hook


@hook('init_complete')
def init_complete(supervisor):
    bottle.BaseTemplate.defaults['assets'] = supervisor.exts.assets
