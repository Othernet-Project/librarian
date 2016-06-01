import logging
import os
import sys

from bottle import Bottle
from gevent import pywsgi, sleep
from confloader import get_config_path, ConfDict

from .exports import Exports
from .exts import ext_container
from .logs import configure_logger
from .pubsub import PubSub
from .signal_handlers import on_interrupt


class EarlyExit(Exception):

    def __init__(self, message='', exit_code=0):
        super(EarlyExit, self).__init__(message)
        self.exit_code = exit_code


class Supervisor:
    #: Interval of the background loop in seconds. This is the possible
    #: shortest time in between consecutive execution of background tasks.
    LOOP_INTERVAL = 5

    #: Default name of the application configuration file.
    DEFAULT_CONFIG_FILENAME = 'config.ini'

    #: Default configuration.
    CONFIG_DEFAULTS = {
        'autojson': True,
        'catchall': True
    }

    # Aliases for system events

    #: Component is initializing
    INITIALIZE = 'initialize'

    #: Component finished loading
    COMPONENT_MEMBER_LOADED = 'component_member_loaded'

    #: All components finished loading
    INIT_COMPLETE = 'init_complete'

    #: Server is about to start
    PRE_START = 'pre_start'

    #: Server has started
    POST_START = 'post_start'

    #: New background loop cycle
    BACKGROUND = 'background'

    #: Server is about to go down
    SHUTDOWN = 'shutdown'

    #: Server is about to go down in an emergency
    IMMEDIATE_SHUTDOWN = 'immediate_shutdown'

    #: List of all events
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

    #: Name of the root package that contains the supervisor
    ROOT_PKG = __name__.split('.')[0]

    EarlyExit = EarlyExit

    def __init__(self, root_dir):
        self.server = None
        self.app = self.wsgi = Bottle()
        self.app.supervisor = self
        self.exts = ext_container
        self.configure(root_dir)
        self.configure_logger()
        self.exts.events = PubSub()
        self.exts.exports = Exports(self)
        self.exts.exports.load_components()
        self.exts.exports.process_components()
        self.handle_interrupt()
        self.running = True
        self.finalize()

    def load_config(self, path, strict=True):
        path = os.path.abspath(path)
        if not strict and not os.path.exists(path):
            return ConfDict()
        return ConfDict.from_file(path, defaults=self.CONFIG_DEFAULTS)

    def merge_config(self, config):
        # merge component config into global config, but without overwriting
        # existing data
        self.config.setdefaults(config)

    def configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        self.config = self.app.config = self.load_config(self.config_path)
        self.config['root'] = root_dir
        self.exts.config = self.config

    def configure_logger(self):
        configure_logger(self.config)

    def handle_interrupt(self):
        """
        Register INT signal handler.
        """
        on_interrupt(self.halt)

    def enter_background_loop(self):
        """
        Keep emitting the :py:attr:`~Supervisor.BACKGROUND` event as long as
        :py:attr:`~Supervisor.running` flag is ``True``. The interval in which
        the events are emitted is roughly :py:attr:`~Supervisor.LOOP_INTERVAL`
        seconds.
        """
        while self.running:
            sleep(self.LOOP_INTERVAL)
            # Fire background event
            self.exts.events.publish(self.BACKGROUND, self)

    def finalize(self):
        """
        Finalize supervisor's initialization and announce the
        :py:attr:`~Supervisor.INIT_COMPLETE` event.

        If any of the components raise an :py:exc:`EarlyExit` exception during
        this stage, the system will exit. This exception is a normal
        flow-control mechanism, not an error condition.

        Exceptions other than :py:exc:`EarlyExit` are logged and reraised.
        """
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

    def start(self):
        # Fire pre-start event right before starting the WSGI server.
        self.exts.events.publish(self.PRE_START, self)
        host = self.config['app.bind']
        port = self.config['app.port']
        self.server = pywsgi.WSGIServer((host, port), self.wsgi, log=None)
        self.server.start()  # non-blocking
        assert self.server.started, 'Expected server to be running'
        logging.debug("Started server on http://%s:%s/", host, port)
        print('Started server on http://%s:%s/' % (host, port))
        # Fire post-start event after WSGI server is started.
        self.exts.events.publish(self.POST_START, self)
        # Start background loop
        self.enter_background_loop()

    def halt(self):
        logging.info('Stopping the application.')
        self.running = False
        self.server.stop(5)
        logging.info('Running shutdown hooks.')
        self.exts.events.publish(self.SHUTDOWN, self)
        logging.info('Clean shutdown.')
