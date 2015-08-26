import getpass

from .helpers import create_user, UserAlreadyExists, InvalidUserCredentials


def create_superuser(supervisor):
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
    except UserAlreadyExists:
        print("User already exists, please try a different username.")
        create_superuser(supervisor)
    except InvalidUserCredentials:
        print("Invalid user credentials, please try again.")
        create_superuser(supervisor)

    raise supervisor.EarlyExit()
