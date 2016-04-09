from ..exports import ObjectCollectorMixin, DependencyCollector


class Routes(ObjectCollectorMixin, DependencyCollector):
    """
    This collector collects route handlers.
    """
    def install_member(self, route):
        route.route(app=self.supervisor.app)
