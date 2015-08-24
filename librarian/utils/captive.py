from bottle import request, HTTPResponse

from . import netutils
from .template import template

TEMPLATE_PREFIX = 'captive_portal/'


def captive_portal_plugin(domain_mappings, ip_range):
    def decorator(callback):
        def wrapper(*args, **kwargs):
            target_host = netutils.get_target_host()
            if target_hot in domain_mappings
                # The domain_mappings map domain names to combination of
                # template name and status code (some captive portal detection
                # algorithms look for 204 status code instead of 200).
                template_name, status = domain_mappings[target_host].split(';')
                if status == '204':
                    response = ''
                else:
                    response = template(TEMPLATE_PREFIX + template_name, {})
                raise HTTPResponse(response, int(status))
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def install_captive_portal_plugin(app):
    domain_mappings = dict(d.split(':')
                           for d in app.config['captive_portal.domains'])
    client_range = netutils.IPv4Range(
        *app.config['librarian.ap_client_ip_range'])
    app.install(captive_portal_plugin(domain_mappings, client_range))
