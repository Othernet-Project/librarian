from ..exports import ObjectCollectorMixin, DependencyCollector


class Middleware(ObjectCollectorMixin, DependencyCollector):
    """
    This collector collects WSGI middleware. WSGI middleware are installed in
    reverse order such that the last-installed (first-registered) middleware
    becomes the outermost (first to handle the request) in the middleware
    stack.
    """
    reverse_order = True

    def install_member(self, middleware):
        self.supervisor.wsgi = middleware(self.supervisor.wsgi)
