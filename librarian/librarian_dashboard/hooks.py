import importlib

from .collector import install_dashboard_plugins, collect_dashboard_plugin


def component_member_loaded(supervisor, member, config):
    mod_path = '{0}.dashboard_plugin'.format(member['pkg_name'])
    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        pass  # no dashboard plugin in this component
    else:
        plugin_cls = getattr(mod, 'Dashboard')
        collect_dashboard_plugin(plugin_cls)


def init_complete(supervisor):
    install_dashboard_plugins(supervisor)
