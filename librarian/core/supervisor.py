import logging
import os
import sys

from bottle import Bottle
from gevent import pywsgi, sleep
from confloader import get_config_path, ConfDict

from .dependencies import DependencyLoader
from .exts import ext_container
from .logs import configure_logger
from .pubsub import PubSub
from .signal_handlers import on_interrupt


class EarlyExit(Exception):

    def __init__(self, message='', exit_code=0):
        super(EarlyExit, self).__init__(message)
        self.exit_code = exit_code


class Supervisor:
    LOOP_INTERVAL = 5  # in seconds
    DEFAULT_CONFIG_FILENAME = 'config.ini'
    CONFIG_DEFAULTS = {
        'autojson': True,
        'catchall': True
    }

    INITIALIZE = 'initialize'
    COMPONENT_MEMBER_LOADED = 'component_member_loaded'
    INIT_COMPLETE = 'init_complete'
    PRE_START = 'pre_start'
    POST_START = 'post_start'
    BACKGROUND = 'background'
    SHUTDOWN = 'shutdown'
    IMMEDIATE_SHUTDOWN = 'immediate_shutdown'
    APP_HOOKS = (
        INITIALIZE,
        COMPONENT_MEMBER_LOADED,
        INIT_COMPLETE,
        PRE_START,
        POST_START,
        BACKGROUND,
        SHUTDOWN,
        IMMEDIATE_SHUTDOWN,
    )
    CORE_COMPONENTS = (
        'assets',
        'system',
        'commands',
        'databases',
        'sessions',
        'auth',
        'i18n',
        'cache',
        'tasks',
        'templates',
    )

    EarlyExit = EarlyExit

    def __init__(self, root_dir):
        self.server = None
        self.app = self.wsgi = Bottle()
        self.app.supervisor = self
        self.exts = ext_container
        self.exts.events = PubSub()

        # Load core configuration
        self._configure(root_dir)
        configure_logger(self.config)

        # Load components
        self._load_components()

        # Register interrupt handler
        on_interrupt(self.halt)

        # Set flag indicating that supervisor is running
        self._running = True

        try:
            # Fire init-complete event. Command line handlers should be
            # executed at this point.
            self.exts.events.publish(self.INIT_COMPLETE, self)
        except EarlyExit as exc:
            # One of the command line handlers probably requested early exit
            sys.exit(exc.exit_code)
        except Exception:
            logging.exception("An error occurred during `init_complete`.")
            raise

    def _load_config(self, path, strict=True):
        path = os.path.abspath(path)
        if not strict and not os.path.exists(path):
            return ConfDict()
        return ConfDict.from_file(path, defaults=self.CONFIG_DEFAULTS)

    def _merge_config(self, config):
        # merge component config into global config, but without overwriting
        # existing data
        self.config.setdefaults(config)

    def _configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        self.config = self.app.config = self._load_config(self.config_path)
        self.config['root'] = root_dir
        self.exts.config = self.config

    def _install_hook(self, name, fn, **kwargs):
        self.exts.events.subscribe(name, fn)
        # the initialize hook must be fired immediately in the scope to
        # which it belongs only
        if name == self.INITIALIZE:
            self.exts.events.publish(name, self, scope=kwargs['mod_name'])

    def _install_routes(self, fn, **kwargs):
        route_config = fn(self.config)
        for route in route_config:
            (name, handler, method, path, kwargs) = route
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

    def _get_core_components(self):
        """Return list of import paths for all found core components."""
        return ['.'.join([__package__, 'contrib', name])
                for name in self.CORE_COMPONENTS]

    def _install_component_member(self, member):
        handler = self.COMPONENT_META[member['type']]['handler']
        config_path = os.path.join(member['pkg_path'],
                                   self.DEFAULT_CONFIG_FILENAME)
        config = self.config.import_from_file(config_path, as_defaults=True,
                                              ignore_missing=True)
        handler(self, **member)
        # notify possibly other components that a new component has been
        # installed successfully
        self.exts.events.publish(self.COMPONENT_MEMBER_LOADED,
                                 self,
                                 member=member,
                                 config=config)
        logging.debug("LOADED: {0}".format('::'.join([member['pkg_path'],
                                                      member['name']])))

    def _load_components(self):
        components = self.config['app.components'] or []
        # add root package to the beginning of the list
        pkg_name = __name__.split('.')[0]
        components = [pkg_name] + components
        # load default core components if core override flag was not set
        if not self.config.get('app.core_override'):
            core_components = self._get_core_components()
            components = core_components + components

        loader = DependencyLoader(components, self.COMPONENT_META)
        for member in loader.load():
            try:
                self._install_component_member(member)
            except Exception:
                logging.exception('Component member installation failed.')

    def _enter_background_loop(self):
        while self._running:
            sleep(self.LOOP_INTERVAL)
            # Fire background event
            self.exts.events.publish(self.BACKGROUND, self)

    def start(self):
        # Fire pre-start event right before starting the WSGI server.
        self.exts.events.publish(self.PRE_START, self)
        host = self.config['app.bind']
        port = self.config['app.port']
        self.server = pywsgi.WSGIServer((host, port), self.wsgi, log=None)
        self.server.start()  # non-blocking
        assert self.server.started, 'Expected server to be running'
        logging.debug("Started server on http://%s:%s/", host, port)
        if self.config['app.debug']:
            print('Started server on http://%s:%s/' % (host, port))

        # Fire post-start event after WSGI server is started.
        self.exts.events.publish(self.POST_START, self)
        # Start background loop
        self._enter_background_loop()

    def halt(self):
        logging.info('Stopping the application.')
        self._running = False
        self.server.stop(5)
        logging.info('Running shutdown hooks.')
        self.exts.events.publish(self.SHUTDOWN, self)
        logging.info('Clean shutdown.')
