import logging
import os
import sys
import time

from bottle import Bottle
from gevent import pywsgi

from .confloader import get_config_path, ConfDict
from .dependencies import DependencyLoader
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

    INIT_BEGIN = 'init_begin'
    INIT_COMPLETE = 'init_complete'
    PRE_START = 'pre_start'
    POST_START = 'post_start'
    BACKGROUND = 'background'
    SHUTDOWN = 'shutdown'
    IMMEDIATE_SHUTDOWN = 'immediate_shutdown'
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

        # Load core configuration
        config_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self._configure(get_config_path(default=config_path))
        self.config['root'] = root_dir

        # Load components
        self._load_components(self.config['app.components'])

        # Fire init-begin event. Subscribers may register command line handlers
        # during this period.
        self.events.publish(self.INIT_BEGIN, self)

        # Register interrupt handler
        on_interrupt(self.halt)

        try:
            # Fire init-complete event. Command line handlers should be
            # executed at this point.
            self.events.publish(self.INIT_COMPLETE, self)
        except EarlyExit as exc:
            # One of the command line handlers probably requested early exit
            sys.exit(exc.exit_code)

    def _configure(self, path):
        path = os.path.abspath(path)
        base_path = os.path.dirname(path)
        self.config = self.app.config = ConfDict.from_file(path,
                                                           base_dir=base_path,
                                                           catchall=True,
                                                           autojson=True)

    def _install_hook(self, name, fn, **kwargs):
        self.events.subscribe(name, fn)

    def _install_routes(self, fn, **kwargs):
        route_config = fn(self.config)
        for route in route_config:
            (path, method, handler, name, kwargs) = route
            self.app.route(path, method, handler, name=name, **kwargs)

    def _install_plugin(self, fn, **kwargs):
        plugin = fn(self)
        self.app.install(plugin)

    COMPONENT_META = {
        'hooks': {
            'exports': dict(zip(APP_HOOKS, [{}] * len(APP_HOOKS))),
            'is_strict': False,
            'handler': _install_hook
        },
        'plugins': {
            'exports': {
                'plugin': {}
            },
            'is_strict': True,
            'handler': _install_plugin
        },
        'routes': {
            'exports': {
                'routes': {}
            },
            'is_strict': True,
            'handler': _install_routes
        }
    }

    def _load_components(self, components):
        loader = DependencyLoader(components, self.COMPONENT_META)
        for dep in loader.load():
            comp_handler = self.COMPONENT_META[dep['type']]['handler']
            comp_handler(**dep)

    def _enter_background_loop(self):
        while True:
            time.sleep(self.LOOP_INTERVAL)
            # Fire background event
            self.events.publish(self.BACKGROUND, self)

    def start(self):
        # Fire pre-start event right before starting the WSGI server.
        self.events.publish(self.PRE_START, self)
        host = self.config['app.bind']
        port = self.config['app.port']
        self.server = pywsgi.WSGIServer((host, port), self.app, log=None)
        self.server.start()  # non-blocking
        assert self.server.started, 'Expected server to be running'
        logging.debug("Started server on http://%s:%s/", host, port)
        if self.config['app.debug']:
            print('Started server on http://%s:%s/' % (host, port))

        # Fire post-start event after WSGI server is started.
        self.events.publish(self.POST_START, self)
        # Start background loop
        self._enter_background_loop()

    def halt(self):
        logging.info('Stopping the application')
        self.server.stop(5)
        logging.info('Running shutdown hooks')
        self.events.publish(self.SHUTDOWN, self)
