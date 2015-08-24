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


def init_begin(supervisor):
    supervisor.app.install(bottle.JSONPlugin(json_dumps=json_dumps))
    supervisor.exts.commands.register('debug',
                                      None,
                                      '--debug',
                                      action='store_true',
                                      help='enable debugging')

    bottle.debug(supervisor.config['app.debug'])
    template_root = os.path.join(supervisor.config['root'],
                                 supervisor.config['app.view_path'])
    bottle.TEMPLATE_PATH.insert(0, template_root)
    bottle.BaseTemplate.defaults.update({
        'DEBUG': bottle.DEBUG,
        'request': bottle.request,
        'h': bottle_utils.html,
        'url': supervisor.app.get_url,
        'csrf_tag': bottle_utils.csrf.csrf_tag,
        '_': lambda x: x,
        'REDIRECT_DELAY': supervisor.config['app.redirect_delay'],
    })
