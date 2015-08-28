import importlib

from .menu import discover_menu_items


def component_member_loaded(supervisor, member, config):
    mod_path = '{0}.menuitems'.format(member['pkg_name'])
    try:
        importlib.import_module(mod_path)
    except ImportError:
        pass  # no menuitems defined in this component


def init_complete(supervisor):
    discover_menu_items(supervisor.config)
