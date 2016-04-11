import logging
import argparse

from ..utils import hasmethod
from ..exports import ObjectCollectorMixin, ListCollector, to_list


class Commands(ObjectCollectorMixin, ListCollector):
    """
    This class manages command argument handlers.
    """
    export_key = 'commands'

    def __init__(self, supervisor):
        super(Commands, self).__init__(supervisor)
        self.parser = argparse.ArgumentParser()
        self.handlers = {}

    def install_member(self, handler):
        name = handler.name
        if name in self.handlers:
            existing = self.handlers[name]
            logging.warn('Duplicate registration for command {}: handler {} '
                         'is already using this name'.format(name, existing))
            return
        self.handlers[name] = handler
        # Build add_argument() args.
        kwargs = handler.kwargs.copy()
        kwargs['dest'] = name
        # Ensure flags are positional arguments and are a list
        args = to_list(handler.flags)
        self.parser.add_argument(*args, **kwargs),
        for arg in handler.extra_args:
            arg = arg.copy()
            # Flags should be positional args, so we have to remove from the
            # kwargs and process them a bit.
            flags = arg.pop('flags', [])
            flags = to_list(flags)
            self.parser.add_argument(*flags, **arg)

    def post_install(self):
        args = self.parser.parse_args()
        arglist = list(vars(args).keys())
        for name, handler in self.handlers:
            if name not in arglist:
                continue
            if hasmethod(handler, 'run'):
                # This is probably a class-based handler
                handler = handler()
                handler.run(args)
            else:
                handler(args)
