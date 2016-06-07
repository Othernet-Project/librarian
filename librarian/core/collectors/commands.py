import inspect
import logging
import argparse

from ..utils.collectors import hasmethod
from ..exts import ext_container as exts
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
        kwargs = getattr(handler, 'kwargs', {}).copy()
        kwargs['dest'] = name
        # Ensure flags are positional arguments and are a list
        args = to_list(handler.flags)
        self.parser.add_argument(*args, **kwargs),
        for arg in getattr(handler, 'extra_arguments', []):
            arg = arg.copy()
            # Flags should be positional args, so we have to remove from the
            # kwargs and process them a bit.
            flags = arg.pop('flags', [])
            flags = to_list(flags)
            self.parser.add_argument(*flags, **arg)

    def post_install(self):
        args = self.parser.parse_args()
        exts.config['args'] = args
        arglist = list(vars(args).keys())
        for name, handler in self.handlers.items():
            # Some command handlers have no actual function to run, but may
            # serve only for collecting some parameters
            if not getattr(arglist, name, None) or not handler:
                continue
            is_class = inspect.isclass(handler)
            if is_class and hasmethod(handler, 'run'):
                # This is probably a class-based handler
                handler = handler()
                handler.run(args)
            elif is_class:
                # This is a class based handler without a `run` method
                continue
            else:
                handler(args)
