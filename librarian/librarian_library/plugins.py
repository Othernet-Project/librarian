from functools import wraps

from bottle import request, redirect

from .helpers import get_content_url
from .netutils import IPv4Range, get_target_host


EXPORTS = {
    'content_resolver_plugin': {}
}


def content_resolver_plugin(supervisor):
    """Load content based on the requested domain"""
    root_url = supervisor.config['app.root_url'],
    ip_range = IPv4Range(*supervisor.config['app.ap_client_ip_range'])

    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            target_host = get_target_host()
            is_regular_access = target_host in root_url
            if not is_regular_access and request.remote_addr in ip_range:
                # a content domain was entered(most likely), try to load it
                content_url = get_content_url(root_url, target_host)
                return redirect(content_url)
            return callback(*args, **kwargs)
        return wrapper
    return decorator
