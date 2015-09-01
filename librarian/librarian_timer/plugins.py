from .timer import request_timer


EXPORTS = {
    'total_timer_plugin': {},
    'handler_timer_plugin': {}
}


def total_timer_plugin(super):
    return request_timer('Total')


def handler_timer_plugin(app):
    return request_timer('Handler')
