import logging

from ..exports import DependencyCollector


class Middleware(DependencyCollector):
    """
    This collector collects WSGI middleware. WSGI middleware are installed in
    reverse order such that the last-installed (first-registered) middleware
    becomes the outermost (first to handle the request) in the middleware
    stack.
    """
    reverse_order = True

    def collect(self, component):
        middleware = component.get_export('middleware', [])
        for m in middleware:
            try:
                mwcls = component.get_object(m)
            except ImportError:
                logging.exception('Failed to import middleware {}'.format(m))
                continue
            self.register(mwcls)

    def install_member(self, middleware):
        self.supervisor.wsgi = middleware(self.supervisor.wsgi)
