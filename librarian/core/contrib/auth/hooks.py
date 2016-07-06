from ...exports import hook
from .plugins import store_user_in_session


@hook('initialize')
def initialize(supervisor):
    supervisor.app.add_hook('after_request', store_user_in_session)
