import importlib

from .collector import install_dashboard_plugins, collect_dashboard_plugin


def component_loaded(supervisor, component, config):
    name = component['pkg_name']
    mod_path = '{0}.dashboard_plugin'.format(name)
    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        pass  # no dashboard plugins in this component
    else:
        collect_dashboard_plugin(name, mod)


def init_begin(supervisor):
    install_dashboard_plugins(supervisor)
