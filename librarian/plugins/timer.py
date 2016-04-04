from .timer import request_timer


EXPORTS = {
    'total_timer_plugin': {},
    'handler_timer_plugin': {}
}


def total_timer_plugin(supervisor):
    return request_timer('Total')


def handler_timer_plugin(supervisor):
    return request_timer('Handler')
