import getpass

from ...exceptions import EarlyExit
from ...exts import ext_container as exts
from .users import User

try:
    input = raw_input
except NameError:
    pass


class NoAuthentication(object):
    name = 'no_auth'
    flags = '--no-auth'
    kwargs = {
        'action': 'store_true',
        'help': 'disable authentication'
    }


class CreateSuperuserCommand(object):
    name = 'su'
    flags = '--su'
    kwargs = {
        'action': 'store_true'
    }
    #: Name of the database used for authentication data
    DATABASE_NAME = 'auth'

    def run(self, args):
        exts.events.subscribe('exp.dbready', self.db_ready)

    def db_ready(self, name, db):
        if name == self.DATABASE_NAME:
            self.create_user()

    def create_user(self):
        print("Press ctrl-c to abort")
        try:
            username = input('Username: ')
            password = getpass.getpass()
        except (KeyboardInterrupt, EOFError):
            print("Aborted")
            raise EarlyExit("Aborted", exit_code=1)

        try:
            user = User.create(username=username,
                               password=password,
                               is_superuser=True,
                               db=exts.databases[self.DATABASE_NAME])
            print("User created. The password reset token is: {}".format(
                user.reset_token))
        except User.InvalidUserCredentials:
            print("Invalid user credentials, please try again.")
            self.create_user()
        else:
            raise EarlyExit()
