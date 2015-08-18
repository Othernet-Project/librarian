import importlib
import logging
import os
import sys
import time

from bottle import Bottle
from gevent import pywsgi

from .confloader import get_config_path, ConfDict
from .exts import ExtContainer
from .pubsub import PubSub
from .signal_handlers import on_interrupt


class EarlyExit(Exception):

    def __init__(self, message, exit_code=0):
        super(EarlyExit, self).__init__(message)
        self.exit_code = exit_code


class Supervisor:
    LOOP_INTERVAL = 5  # in seconds
    DEFAULT_CONFIG_FILENAME = 'librarian.ini'

    INIT_BEGIN = 'INIT_BEGIN'
    INIT_COMPLETE = 'INIT_COMPLETE'
    PRE_START = 'PRE_START'
    POST_START = 'POST_START'
    BACKGROUND = 'BACKGROUND'
    SHUTDOWN = 'SHUTDOWN'
    IMMEDIATE_SHUTDOWN = 'IMMEDIATE_SHUTDOWN'
    APP_HOOKS = (
        INIT_BEGIN,
        INIT_COMPLETE,
        PRE_START,
        POST_START,
        BACKGROUND,
        SHUTDOWN,
        IMMEDIATE_SHUTDOWN,
    )

    EarlyExit = EarlyExit

    def __init__(self, root_dir):
        self.server = None
        self.app = Bottle()
        self.events = PubSub()
        self.exts = ExtContainer()

        # Load configuration
        config_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.configure(get_config_path(default=config_path))
        self.config['root'] = root_dir

        # Register application hooks
        for hook_name in self.APP_HOOKS:
            self.add_hooks(hook_name)

        # Fire init-begin event. Subscribers may register command line handlers
        # during this period.
        self.events.publish(self.INIT_BEGIN, self)

        # Register higher-level components
        self.add_plugins(self.config['stack.plugins'])
        self.add_routes(self.config['stack.routes'])

        # Register interrupt handler
        on_interrupt(self.halt)

        try:
            # Fire init-complete event. Command line handlers should be
            # executed at this point.
            self.events.publish(self.INIT_COMPLETE, self)
        except EarlyExit as exc:
            # One of the command line handlers probably requested early exit
            sys.exit(exc.exit_code)

    def configure(self, path):
        path = os.path.abspath(path)
        base_path = os.path.dirname(path)
        self.config = self.app.config = ConfDict.from_file(path,
                                                           base_dir=base_path,
                                                           catchall=True,
                                                           autojson=True)

    def add_hooks(self, hook_name):
        for hook_path in self.config.get('stack.{0}'.format(hook_name), []):
            hook = self._import(hook_path)
            self.events.subscribe(hook_name, hook)

    def add_plugins(self, plugins):
        for plugin in plugins:
            plugin = self._import(plugin)
            self.app.install(plugin(self.config))

    def add_routes(self, routing):
        for route in routing:
            route = self._import(route)
            for r in route(self.config):
                path, method, cb, name, kw = r
                self.app.route(path, method, cb, name=name, **kw)

    def start(self):
        # Fire pre-start event right before starting the WSGI server.
        self.events.publish(self.PRE_START, self)
        host = self.config['server.bind']
        port = self.config['server.port']
        self.server = pywsgi.WSGIServer((host, port), self.app, log=None)
        self.server.start()  # non-blocking
        assert self.server.started, 'Expected server to be running'
        logging.debug("Started server on http://%s:%s/", host, port)
        if self.config['server.debug']:
            print('Started server on http://%s:%s/' % (host, port))

        # Fire post-start event after WSGI server is started.
        self.events.publish(self.POST_START, self)
        # Start background loop
        self.init_background()

    def init_background(self):
        while True:
            time.sleep(self.LOOP_INTERVAL)
            # Fire background event
            self.events.publish(self.BACKGROUND, self)

    def halt(self):
        logging.info('Stopping the application')
        self.server.stop(5)
        logging.info('Running shutdown hooks')
        self.events.publish(self.SHUTDOWN, self)

    @staticmethod
    def _import(name):
        mod, obj = name.rsplit('.', 1)
        mod = importlib.import_module(mod)
        return getattr(mod, obj)
