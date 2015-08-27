import importlib

import bottle

from .menu import MenuItem, menu_group, menu_item, MENU_ITEMS, MENU_GROUPS


def component_loaded(supervisor, component, config):
    mod_path = '{0}.menuitems'.format(component['pkg_name'])
    try:
        importlib.import_module(mod_path)
    except ImportError:
        pass  # no menuitems defined in this component


def init_begin(supervisor):
    menu_item_classes = MenuItem.__subclasses__()

    for (name, group) in supervisor.config.items():
        if not name.startswith('menu.'):
            continue
        group_name = name.replace('menu.', '')

        for item_name in group:
            menu_cls = [cls for cls in menu_item_classes
                        if cls.name == item_name]
            MENU_ITEMS.append(menu_cls)
            MENU_GROUPS.setdefault(group_name, [])
            MENU_GROUPS[group_name].append(menu_cls)

    bottle.BaseTemplate.defaults.update({'menu_group': menu_group,
                                         'menu_item': menu_item})
