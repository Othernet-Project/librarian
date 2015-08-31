import getpass

from .helpers import create_user, InvalidUserCredentials


def create_superuser(arg, supervisor):
    print("Press ctrl-c to abort")
    try:
        username = raw_input('Username: ')
        password = getpass.getpass()
    except (KeyboardInterrupt, EOFError):
        print("Aborted")
        raise supervisor.EarlyExit("Aborted", exit_code=1)

    try:
        reset_token = create_user(username=username,
                                  password=password,
                                  is_superuser=True,
                                  db=supervisor.exts.databases.sessions,
                                  overwrite=True)
        print("User created. The password reset token is: {}".format(
            reset_token))
    except InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser(arg, supervisor)

    raise supervisor.EarlyExit()
