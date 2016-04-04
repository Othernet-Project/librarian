from .version import get_version


def display_version(arg, supervisor):
    ver = get_version(supervisor.config)
    print('v%s' % ver)
    raise supervisor.EarlyExit()
