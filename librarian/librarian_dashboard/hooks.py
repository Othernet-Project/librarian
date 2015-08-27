import importlib

from .collector import install_dashboard_plugins, collect_dashboard_plugin


def component_loaded(supervisor, component, config):
    mod_path = '{0}.dashboard_plugin'.format(component['pkg_name'])
    try:
        mod = importlib.import_module(mod_path)
    except ImportError:
        pass  # no dashboard plugin in this component
    else:
        plugin_cls = getattr(mod, 'Dashboard')
        collect_dashboard_plugin(plugin_cls)


def init_begin(supervisor):
    install_dashboard_plugins(supervisor)
