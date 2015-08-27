from .timer import request_timer


def total_timer_plugin(super):
    return request_timer('Total')


def handler_timer_plugin(app):
    return request_timer('Handler')
