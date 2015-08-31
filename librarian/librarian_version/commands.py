from librarian import __version__

from .version import get_version


def display_version(arg, supervisor):
    ver = get_version(__version__, supervisor.config)
    print('v%s' % ver)
    raise supervisor.EarlyExit()
