from .bottleconf import install_view_root, configure_bottle


def component_member_loaded(supervisor, member, config):
    pkg_path = member['pkg_path']
    view_path = config.pop('templates.view_path', None)
    if view_path:
        install_view_root(pkg_path, view_path)


def initialize(supervisor):
    configure_bottle(supervisor)
    # add shared template root if it exists
    view_path = supervisor.config.get('templates.view_path', None)
    if view_path:
        install_view_root(supervisor.config['root'], view_path)
