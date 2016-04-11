from ..exports import ObjectCollectorMixin, DependencyCollector


class Plugins(ObjectCollectorMixin, DependencyCollector):
    """
    This collector collects Bottle plugins. All plugins are installed in
    reverse order. This ensures that the last-installed plugin is invoked first
    when handling requests.
    """
    export_key = 'plugins'
    reverse_order = True

    def install_member(self, plugin):
        self.supervisor.app.install(plugin)
