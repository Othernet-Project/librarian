import datetime
import json
import os

import bottle

import bottle_utils.csrf
import bottle_utils.html


class DateTimeCapableEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return super(DateTimeCapableEncoder, self).default(obj)


def json_dumps(s):
    return json.dumps(s, cls=DateTimeCapableEncoder)


def install_view_root(pkg_path, view_path):
    template_root = os.path.join(pkg_path, view_path)
    bottle.TEMPLATE_PATH.insert(0, template_root)


def configure_bottle(supervisor):
    supervisor.app.install(bottle.JSONPlugin(json_dumps=json_dumps))
    bottle.debug(supervisor.config['app.debug'])
    bottle.BaseTemplate.defaults.update({
        'DEBUG': bottle.DEBUG,
        'request': bottle.request,
        'h': bottle_utils.html,
        'url': supervisor.app.get_url,
        'csrf_tag': bottle_utils.csrf.csrf_tag,
        '_': lambda x: x,
        'REDIRECT_DELAY': supervisor.config['app.redirect_delay'],
    })
