from ...exports import hook
from .plugins import save_session


@hook('initialize')
def initialize(supervisor):
    supervisor.app.add_hook('after_request', save_session)
