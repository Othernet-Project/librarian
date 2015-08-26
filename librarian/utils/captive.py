import logging

from bottle import request, HTTPResponse, redirect

from . import netutils
from .template import template

TEMPLATE_PREFIX = 'captive_portal/'


def captive_portal_plugin(domain_mappings, ip_range, self_url):
    def decorator(callback):
        def wrapper(*args, **kwargs):
            target_host = netutils.get_target_host()

            if target_host not in domain_mappings:
                # This is not a captive portal check
                logging.debug('No captive portal match for %s', target_host)
                return callback(*args, **kwargs)

            logging.debug('Matched captive portal host %s', target_host)

            # The domain_mappings map domain names to combination of
            # template name and status code (some captive portal detection
            # algorithms look for 204 status code instead of 200).
            template_name, status = domain_mappings[target_host].split(';')

            if status == '204':
                response = ''
            elif status == '302':
                return redirect(self_url, 302)
            else:
                response = template(TEMPLATE_PREFIX + template_name, {})
            raise HTTPResponse(response, int(status))
        return wrapper
    return decorator


def install_captive_portal_plugin(app):
    domain_mappings = dict(d.split(':')
                           for d in app.config['captive_portal.domains'])
    client_range = netutils.IPv4Range(
        *app.config['librarian.ap_client_ip_range'])
    self_url = app.config['librarian.root_url'] + '/'
    app.install(captive_portal_plugin(domain_mappings, client_range, self_url))
