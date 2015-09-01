from .bottleconf import install_view_root, configure_bottle


def component_member_loaded(supervisor, member, config):
    pkg_path = member['pkg_path']
    directory = config.pop('templates.directory', None)
    if directory:
        install_view_root(pkg_path, directory)


def initialize(supervisor):
    configure_bottle(supervisor)
    # add shared template root if it exists
    directory = supervisor.config.get('templates.directory', None)
    if directory:
        install_view_root(supervisor.config['root'], directory)
