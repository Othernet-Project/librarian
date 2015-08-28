from .commands import refill_db, reload_db
from .utils import ensure_dir


def initialize(supervisor):
    ensure_dir(supervisor.config['library.spooldir'])
    ensure_dir(supervisor.config['library.unpackdir'])
    ensure_dir(supervisor.config['library.contentdir'])

    supervisor.exts.commands.register(
        'refill',
        refill_db,
        '--refill',
        action='store_true',
        help="Empty database and then reload zipballs into it."
    )
    supervisor.exts.commands.register(
        'reload',
        reload_db,
        '--reload',
        action='store_true',
        help="Reload zipballs into database without clearing it previously."
    )
