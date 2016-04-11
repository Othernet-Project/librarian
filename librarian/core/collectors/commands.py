import logging
import argparse

from ..exports import ListCollector, to_list


class Commands(ListCollector):
    """
    This class manages command argument handlers.
    """
    def __init__(self, supervisor):
        super(Commands, self).__init__(supervisor)
        self.parser = argparse.ArgumentParser()
        self.handlers = {}

    def collect(self, component):
        commands = component.get_export('commands', [])
        for command in commands:
            try:
                handler = component.get_object(command)
            except ImportError:
                logging.exception('Could not import handler')
                continue
            if not hasattr(handler, 'name'):
                logging.error('Invalid handler {} for component {}'.format(
                    command, component.name))
                continue
            handler.component = component.name
            self.register(handler)

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
            if name in arglist:
                handler(args)
