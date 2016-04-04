from .registry import MenuItemRegistry


def initialize(supervisor):
    supervisor.exts.menuitems = MenuItemRegistry()


def init_complete(supervisor):
    supervisor.exts.menuitems.sort(supervisor.config)
