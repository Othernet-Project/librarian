from .commands import dump_tables
from .utils import close_databases, init_databases


def component_member_loaded(supervisor, member, config):
    supervisor.config.setdefault('database.sources', {})
    pkg_name = member['pkg_name']
    if pkg_name not in supervisor.config['database.sources']:
        db_names = config.pop('database.names', None)
        if db_names:
            supervisor.config['database.sources'][pkg_name] = db_names


def initialize(supervisor):
    supervisor.exts.databases = init_databases(supervisor.config)
    supervisor.exts.commands.register('dump_tables',
                                      dump_tables,
                                      '--dump-tables',
                                      action='store_true')


def shutdown(supervisor):
    close_databases(supervisor.exts.databases)


def immediate_shutdown(supervisor):
    close_databases(supervisor.exts.databases)
