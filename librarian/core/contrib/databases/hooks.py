from ...exports import hook
from .helpers import close_databases


@hook('shutdown')
def shutdown(supervisor):
    close_databases()


@hook('immediate_shutdown')
def immediate_shutdown(supervisor):
    close_databases()
