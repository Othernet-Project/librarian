from fsal.client import FSAL

from .commands import refill_facets
from .tasks import check_new_content, scan_facets


SCAN_DELAY = 5
STEP_DELAY = 0.5


def initialize(supervisor):
    supervisor.exts.fsal = FSAL(supervisor.config['fsal.socket'])
    supervisor.exts.commands.register(
        'refill_facets',
        refill_facets,
        '--refill-facets',
        action='store_true',
        help="Empty facets archive and reconstruct it."
    )


def post_start(supervisor):
    config = supervisor.config
    refresh_rate = config['facets.refresh_rate']
    supervisor.exts.tasks.schedule(check_new_content,
                                   args=(supervisor, refresh_rate),
                                   delay=refresh_rate)
    if config.get('facets.scan', False):
        start_delay = config.get('facets.scan_delay', SCAN_DELAY)
        step_delay = config.get('facets.scan_step_delay', STEP_DELAY)
        kwargs = dict(step_delay=step_delay, config=config)
        supervisor.exts.tasks.schedule(scan_facets,
                                       kwargs=kwargs,
                                       delay=start_delay)
