import logging

from squery_pg.squery_pg import DatabaseContainer, Database, migrate

from ..exports import ListCollector, to_list
from ..exts import ext_container as exts


class Databases(ListCollector):
    """
    This class handles database members.
    """
    #: Event name used to signal that a database is ready
    DATABASE_READY = 'exp.dbready'

    def __init__(self, supervisor):
        super(Databases, self).__init__(supervisor)
        self.databases = exts.databases = DatabaseContainer({})
        self.host = exts.config['database.host']
        self.port = exts.config['database.port']
        self.user = exts.config['database.user']
        self.password = exts.config['database.password']
        self.debug = True  # FIXME: get the value from a sane location

    def get_connection(self, dbname):
        """
        Get a connection object for a given database.
        """
        return Database.connect(database=dbname,
                                host=self.host,
                                port=self.port,
                                user=self.user,
                                password=self.password,
                                debug=self.debug)

    def collect(self, component):
        migrations = component.get_export('migrations', default='migrations')
        dbname = component.get_export('database', default=None)
        database_sets = to_list(component.get_export('database_sets',
                                                     default=[]))
        for dbset in database_sets:
            migration_pkg = '{}.{}.{}'.format(component.name, migrations,
                                              dbset)
            self.register((dbname, dbset, migration_pkg, component.name))
            logging.debug('Registered database set {} in {} for {}'.format(
                dbset, dbname, component.name))

    def install_member(self, database):
        dbname, dbset, migrations_pkg, component_name = database
        dbconn = self.get_connection(dbname)
        dbconn.package_name = component_name
        self.databases[dbname] = dbconn
        migrate(dbconn, dbset, migrations_pkg, self.supervisor.config)
        exts.events.publish(self.DATABASE_READY, name=dbset, db=dbconn)
        logging.info('Database set {} installed for {}'.format(
            dbset, component_name))

    @staticmethod
    def get_migrations_name(package_name):
        package_components = package_name.split('.')
        return package_components[-1]
