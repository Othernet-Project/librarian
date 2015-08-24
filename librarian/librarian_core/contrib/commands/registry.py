import argparse
import sys


class CommandLineHandler:

    def __init__(self, supervisor):
        self._supervisor = supervisor
        self._parser = argparse.ArgumentParser()
        self._handlers = {}
        self.args = None

    def register(self, name, fn, *args, **kwargs):
        self._handlers[name] = fn
        self._parser.add_argument(*args, **kwargs)

    def handle(self):
        args = self._parser.parse_args(sys.argv[1:])
        for (name, fn) in self._handlers.items():
            arg = getattr(args, name, None)
            if arg:
                fn(arg, self._supervisor)

        return args
