from ...presentation.menu.registry import MenuItemRegistry
from ..exports import (ObjectCollectorMixin, RegistryInstallerMixin,
                       ListCollector)


class MenuItems(ObjectCollectorMixin, RegistryInstallerMixin, ListCollector):
    """
    This collector collects menu items.
    """
    ext_name = 'menu_items'
    registry_class = MenuItemRegistry
    ext_name = 'menu'
