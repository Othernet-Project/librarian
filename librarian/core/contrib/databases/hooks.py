from squery_pg.squery_pg import DatabaseContainer

from .commands import dump_tables
from .helpers import close_databases, register_database, run_migrations


EXPORTS = {
    'initialize': {
        'depends_on': ['librarian.core.contrib.commands.hooks.initialize']
    },
    'component_member_loaded': {},
    'init_complete': {
        'required_by': ['librarian.core.contrib.commands.hooks.init_complete']
    },
    'shutdown': {},
    'immediate_shutdown': {}
}


def initialize(supervisor):
    supervisor.exts.databases = DatabaseContainer({})
    supervisor.exts.commands.register('dump_tables',
                                      dump_tables,
                                      '--dump-tables',
                                      action='store_true')


def component_member_loaded(supervisor, member, config):
    for dbname in config.get('databases', []):
        register_database(dbname, member['pkg_name'])


def init_complete(supervisor):
    run_migrations()


def shutdown(supervisor):
    close_databases()


def immediate_shutdown(supervisor):
    close_databases()
