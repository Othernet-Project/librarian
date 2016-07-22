import json
import urlparse

from bottle import response

from bottle_utils.csrf import csrf_protect, csrf_token
from bottle_utils.html import set_qparam
from bottle_utils.i18n import i18n_path


class CSRFRouteMixin(object):

    @csrf_token
    def get(self, *args, **kwargs):
        return super(CSRFRouteMixin, self).get(*args, **kwargs)

    @csrf_protect
    def post(self, *args, **kwargs):
        return super(CSRFRouteMixin, self).post(*args, **kwargs)


class RedirectRouteMixin(object):
    next_url_parameter_name = 'next'
    next_context_parameter_name = 'next_path'
    default_next_path = '/'

    def get_next_path(self):
        return self.request.params.get(self.next_url_parameter_name,
                                       self.default_next_path)

    def get_next_url(self):
        next_path = i18n_path(self.get_next_path())
        return urlparse.urljoin(self.request.url, next_path)

    def add_next_parameter(self, base_url):
        next_params = {self.next_url_parameter_name: self.get_next_path()}
        return base_url + set_qparam(**next_params).to_qs()

    def get_default_context(self):
        ctx = super(RedirectRouteMixin, self).get_default_context()
        ctx[self.next_context_parameter_name] = self.get_next_path()
        return ctx

    def perform_redirect(self, url=None, status=303):
        self.response.set_header('Location', url or self.get_next_url())
        self.response.status = status


class JSONResponseMixin(object):
    content_type = 'application/json'

    def create_response(self):
        super(JSONResponseMixin, self).create_response()
        self.body = json.dumps(self.body)
        response.content_type = self.content_type
