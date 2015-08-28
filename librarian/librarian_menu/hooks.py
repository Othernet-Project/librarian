import importlib

from .menu import discover_menu_items


def component_loaded(supervisor, component, config):
    mod_path = '{0}.menuitems'.format(component['pkg_name'])
    try:
        importlib.import_module(mod_path)
    except ImportError:
        pass  # no menuitems defined in this component


def initialize(supervisor):
    discover_menu_items(supervisor.config)
