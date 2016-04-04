from .commands import dump_tables
from .helpers import close_databases, init_databases


EXPORTS = {
    'initialize': {
        'depends_on': ['librarian_core.contrib.commands.hooks.initialize']
    },
    'component_member_loaded': {},
    'init_complete': {
        'required_by': ['librarian_core.contrib.commands.hooks.init_complete']
    },
    'shutdown': {},
    'immediate_shutdown': {}
}


def initialize(supervisor):
    supervisor.exts.commands.register('dump_tables',
                                      dump_tables,
                                      '--dump-tables',
                                      action='store_true')


def component_member_loaded(supervisor, member, config):
    supervisor.config.setdefault('database.sources', {})
    pkg_name = member['pkg_name']
    if pkg_name not in supervisor.config['database.sources']:
        db_names = config.pop('database.names', None)
        if db_names:
            supervisor.config['database.sources'][pkg_name] = db_names


def init_complete(supervisor):
    supervisor.exts.databases = init_databases(supervisor.config)


def shutdown(supervisor):
    close_databases(supervisor.exts.databases)


def immediate_shutdown(supervisor):
    close_databases(supervisor.exts.databases)
