import functools
import logging

from bottle import HTTPResponse, redirect

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..utils import netutils


def captive_portal_plugin(fn):
    domains = exts.config['captive_portal.domains']
    domain_mappings = dict(d.split(':') for d in domains)
    self_url = exts.config['app.root_url'] + '/'

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        target_host = netutils.get_target_host()

        if target_host not in domain_mappings:
            # No domain matches captive portal check
            return fn(*args, **kwargs)

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
            response = template(template_name, {})
        raise HTTPResponse(response, int(status))
    return wrapper
captive_portal_plugin.name = 'captive_portal_plugin'