

class DashboardPluginRegistry(object):

    def __init__(self):
        self.collected = dict()
        self.installed = []

    def register(self, plugin_cls):
        self.collected[plugin_cls.name] = plugin_cls

    def sort(self):
        # Install dashboard plugins for plugins that have them
        self.installed = [i[1]() for i in sorted(self.collected.items(),
                                                 key=lambda c: c[1].priority,
                                                 reverse=True)]

    @property
    def plugins(self):
        return self.installed
