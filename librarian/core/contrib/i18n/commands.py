from .cmsgs import compile_messages
from .xmsgs import collect_messages


class CollectMessagesCommand(object):
    name = 'xmsgs'
    flags = '--xmsgs'
    kwargs = {
        'action': 'store_true',
        'help': 'collect gettext messages'
    }

    def run(self, args):
        return collect_messages()


class CompileMessagesCommand(object):
    name = 'cmsgs'
    flags = '--cmsgs'
    kwargs = {
        'action': 'store_true',
        'help': 'compile gettext messages'
    }

    def run(self, args):
        return compile_messages()
