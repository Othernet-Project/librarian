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

    def run(self, args):
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
                               db=exts.databases.auth)
            print("User created. The password reset token is: {}".format(
                user.reset_token))
        except User.InvalidUserCredentials:
            print("Invalid user credentials, please try again.")
            self.run(args)
        else:
            raise EarlyExit()
