import bottle


class MenuItemNotFound(Exception):
    pass


class MenuItemRegistry(object):

    def __init__(self):
        self.registered = []
        self.items = []
        self.groups = dict()
        bottle.BaseTemplate.defaults.update({'menu_group': self.menu_group,
                                             'menu_item': self.menu_item})

    def menu_group(self, group):
        """Return list of menu items that belong to the specified `group`"""
        for item in self.groups[group]:
            yield item()

    def menu_item(self, name, group=None):
        """Return a single menu item that matches the given name. It looks
        through either the whole list of menu items, or if `group` is
        specified, only on the subset belonging to that group."""
        items = self.menu_group(group) if group else self.items
        for item in items:
            if item.name == name:
                return item()

    def register(self, menu_item_cls):
        self.registered.append(menu_item_cls)

    def sort(self, config):
        for (name, group) in config.items():
            if not name.startswith('menu.') or name == 'menu.items':
                continue
            group_name = name.replace('menu.', '')

            for item_name in group:
                try:
                    (menu_cls,) = [cls for cls in self.registered
                                   if cls.name == item_name]
                except ValueError:
                    raise MenuItemNotFound(item_name)
                else:
                    self.items.append(menu_cls)
                    self.groups.setdefault(group_name, [])
                    self.groups[group_name].append(menu_cls)
