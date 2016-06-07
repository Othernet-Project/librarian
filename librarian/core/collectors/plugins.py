from ..exports import ObjectCollectorMixin, DependencyCollector


class Plugins(ObjectCollectorMixin, DependencyCollector):
    """
    This collector collects Bottle plugins.
    """
    export_key = 'plugins'
    reverse_order = False

    def install_member(self, plugin):
        self.supervisor.app.install(plugin)
