from ..utils.timer import request_timer


total_timer_plugin = request_timer('Total')
total_timer_plugin.name = 'total_timer_plugin'

handler_timer_plugin = request_timer('Handler')
handler_timer_plugin.name = 'handler_timer_plugin'
