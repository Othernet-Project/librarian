from ...exports import hook
from .bottleconf import configure_bottle


@hook('initialize')
def initialize(supervisor):
    configure_bottle(supervisor)
