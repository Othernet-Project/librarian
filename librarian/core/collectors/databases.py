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
        return Database.connect(database=dbname, host=self.host, port=self.port,
                                user=self.user, password=self.password,
                                debug=self.debug)

    def collect(self, component):
        migrations = component.get_export('migrations', default='migrations')
        databases = to_list(component.get_export('databases', default=[]))
        for dbname in databases:
            migration_pkg = '{}.{}.{}'.format(component.name, migrations,
                                              dbname)
            self.register((dbname, migration_pkg, component.name))
            logging.debug('Registered database {} for {}'.format(
                dbname, component.name))

    def install_member(self, database):
        dbname, migrations_pkg, component_name = database
        dbconn = self.get_connection(dbname)
        dbconn.package_name = component_name
        self.databases[dbname] = dbconn
        migrate(dbconn, migrations_pkg, self.supervisor.config)
        exts.events.publish(self.DATABASE_READY, name=dbname, db=dbconn)
        logging.info('Database {} installed for {}'.format(
            dbname, component_name))
